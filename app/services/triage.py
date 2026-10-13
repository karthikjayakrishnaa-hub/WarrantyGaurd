from sqlalchemy.orm import Session
from app.models.claim import Claim, ClaimStatus
from app.models.triage_result import TriageResult
from app.models.audit_log import AuditAction
from app.services.audit import log_action
import time

from app.services import (
    ocr_invoice,
    ocr_label,
    complaint_nlp,
    rule_engine,
    duplicate_detection,
    policy_rag,
    genai_report
)

def triage_claim(db: Session, claim_id: int, progress_callback=None):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        return

    claim_data = {
        "id": claim.id,
        "product_model": claim.product_model,
        "serial_number": claim.serial_number,
        "complaint_text": claim.complaint_text,
    }

    import os
    from app.core.config import settings
    
    def get_local_path(file_name):
        local_path = os.path.join(settings.STORAGE_PATH, file_name)
        if not os.path.exists(local_path):
            from app.core.storage import get_supabase_client
            try:
                supabase = get_supabase_client()
                res = supabase.storage.from_(settings.STORAGE_BUCKET).download(file_name)
                with open(local_path, "wb") as f:
                    f.write(res)
            except Exception as e:
                import logging
                logging.error(f"Failed to download {file_name} from Supabase: {e}")
        return local_path

    from app.models.evidence import EvidenceType
    # Initialize to None — if the user didn't upload one of these evidence types
    # the variable must still exist so the OCR steps below can safely check `if path`.
    # Previously these were uninitialized, causing an UnboundLocalError crash that
    # left the claim permanently stuck in "processing" status.
    invoice_path = None
    label_path = None
    for ev in claim.evidence:
        if ev.type == EvidenceType.invoice:
            invoice_path = get_local_path(ev.file_path)
        elif ev.type == EvidenceType.label_photo:
            label_path = get_local_path(ev.file_path)


    # Step 1: Pre-processing & Fetching
    if progress_callback: progress_callback(1, "Fetching Evidence")
    time.sleep(0.5)

    # 2. Invoice OCR
    if progress_callback: progress_callback(2, "OCR Invoice")
    invoice_data = {}
    if invoice_path:
        invoice_data = ocr_invoice.extract_invoice_fields(invoice_path)

    # 3. Product Label OCR
    if progress_callback: progress_callback(3, "OCR Label")
    label_data = {}
    if label_path:
        label_data = ocr_label.extract_label_info(label_path)

    # 4. Complaint NLP
    if progress_callback: progress_callback(4, "NLP Complaint")
    complaint_data = complaint_nlp.parse_complaint(claim.complaint_text)

    # 5. Warranty Rule Engine
    if progress_callback: progress_callback(5, "Rule Engine")
    rule_data = rule_engine.validate_warranty(db, claim_data, invoice_data, label_data)
    claim_data["rule_data"] = rule_data

    # 6. Duplicate Detection
    if progress_callback: progress_callback(6, "Duplicate Detection")
    is_duplicate = False
    for ev in claim.evidence:
        if ev.phash:
            if duplicate_detection.detect_duplicates(ev.phash, db, claim.id):
                is_duplicate = True
                break
    claim_data["is_duplicate"] = is_duplicate

    # 7. Policy RAG
    if progress_callback: progress_callback(7, "Policy RAG")
    
    from app.models.product import Product
    product = db.query(Product).filter(Product.name.ilike(f"%{claim.product_model}%")).first()
    brand = product.brand if product else "Generic"
    
    policy_data = policy_rag.retrieve_policy_clauses(claim.complaint_text, brand=brand)
    claim_data["policy_clauses"] = policy_data

    image_paths = []
    for ev in claim.evidence:
        if ev.file_path:
            image_paths.append(get_local_path(ev.file_path))

    # 8. GenAI Report & Triage DB Save
    if progress_callback: progress_callback(8, "AI Vision & Triage DB Save")
    report_data = genai_report.generate_review_summary(claim_data, image_paths)

    # Save triage result
    triage_result = db.query(TriageResult).filter(TriageResult.claim_id == claim.id).first()
    if not triage_result:
        triage_result = TriageResult(
            claim_id=claim.id,
            category=report_data["category"],
            reasoning_summary=report_data["reasoning_summary"],
            recommended_action=report_data["recommended_action"]
        )
        db.add(triage_result)
    else:
        triage_result.category = report_data["category"]
        triage_result.reasoning_summary = report_data["reasoning_summary"]
        triage_result.recommended_action = report_data["recommended_action"]

    claim.status = ClaimStatus.triaged
    log_action(db, claim.id, AuditAction.pipeline_completed, claim.user_id,
               f"AI triage completed — category: {report_data['category']}")
    db.commit()
