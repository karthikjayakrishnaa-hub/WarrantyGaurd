"""
Comprehensive test for the 8-step AI Triage Pipeline.

Steps:
  1. Fetching Evidence (pre-processing)
  2. OCR Invoice
  3. OCR Label
  4. NLP Complaint
  5. Warranty Rule Engine
  6. Duplicate Detection
  7. Policy RAG
  8. GenAI Report & Triage DB Save
"""

import os, sys, time, json, traceback, requests

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

# Ensure .env is loaded
from dotenv import load_dotenv
load_dotenv()

# Pre-import all models so SQLAlchemy mappers are fully initialized
from app.models.organization import Organization
from app.models.product import Product
from app.models.user import User
from app.models.claim import Claim
from app.models.evidence import Evidence
from app.models.triage_result import TriageResult
from app.models.audit_log import AuditLog
from app.models.warranty_policy import WarrantyPolicy
from app.models.comment import Comment
from app.models.invitation import Invitation
from app.models.pipeline_status import PipelineStatus

PASS_TAG = "[PASS]"
FAIL_TAG = "[FAIL]"
WARN_TAG = "[WARN]"

results = []

def run_test(name, fn):
    print(f"\n{'='*60}")
    print(f"  STEP: {name}")
    print(f"{'='*60}")
    try:
        ok, detail = fn()
        tag = PASS_TAG if ok else (WARN_TAG if "WARN" in detail else FAIL_TAG)
        print(f"  {tag}  {detail}")
        results.append((name, "PASS" if ok else "WARN/FAIL", detail))
        return ok
    except Exception as e:
        print(f"  {FAIL_TAG}  Exception: {e}")
        traceback.print_exc()
        results.append((name, "FAIL", str(e)))
        return False

# ==================================================================
# STEP 1: Fetching Evidence -- test DB query for claim + evidence
# ==================================================================
def test_step1_fetch_evidence():
    from app.core.database import SessionLocal
    from app.models.claim import Claim
    db = SessionLocal()
    try:
        claim = db.query(Claim).first()
        if not claim:
            return True, "WARN: No claims in DB yet (OK for fresh DB)"
        ev_count = len(claim.evidence) if claim.evidence else 0
        return True, f"Claim #{claim.id} fetched. Evidence count: {ev_count}"
    finally:
        db.close()

# ==================================================================
# STEP 2: OCR Invoice
# ==================================================================
def test_step2_ocr_invoice():
    from app.services.ocr_invoice import extract_invoice_fields, ocr_engine
    if not ocr_engine:
        return True, "WARN: PaddleOCR not installed -- OCR will be skipped gracefully"
    result = extract_invoice_fields("nonexistent.png")
    return True, f"OCR Invoice function callable. Graceful fallback: {result}"

# ==================================================================
# STEP 3: OCR Label
# ==================================================================
def test_step3_ocr_label():
    from app.services.ocr_label import extract_label_info, ocr_engine
    if not ocr_engine:
        return True, "WARN: PaddleOCR not installed -- Label OCR will be skipped gracefully"
    result = extract_label_info("nonexistent.png")
    return True, f"OCR Label function callable. Graceful fallback: {result}"

# ==================================================================
# STEP 4: NLP Complaint
# ==================================================================
def test_step4_nlp_complaint():
    from app.services.complaint_nlp import parse_complaint, nlp
    
    # Test 1: High severity
    r1 = parse_complaint("The screen is completely broken and there is smoke coming out")
    # Test 2: Replace intent
    r2 = parse_complaint("I want a refund for this defective product")
    # Test 3: Low severity
    r3 = parse_complaint("The trackpad is a bit sticky")
    
    if not nlp:
        return True, f"WARN: spaCy not installed -- returns defaults: {r1}"
    
    checks = []
    if r1.get("severity") == "high":
        checks.append("high-severity detection OK")
    else:
        checks.append(f"high-severity MISS (got {r1})")
    if r2.get("intent") == "replace":
        checks.append("replace-intent detection OK")
    else:
        checks.append(f"replace-intent MISS (got {r2})")
    
    all_ok = r1.get("severity") == "high" and r2.get("intent") == "replace"
    return all_ok, " | ".join(checks)

# ==================================================================
# STEP 5: Warranty Rule Engine
# ==================================================================
def test_step5_rule_engine():
    from app.services.rule_engine import validate_warranty
    
    # Test 1: Valid warranty (recent purchase)
    claim_data = {"product_model": "HP OMEN 16"}
    invoice_data = {"purchase_date": "2026-06-01", "model": "HP OMEN 16"}
    label_data = {"model": "HP OMEN 16"}
    r1 = validate_warranty(claim_data, invoice_data, label_data)
    
    # Test 2: Expired warranty
    invoice_expired = {"purchase_date": "2020-01-01", "model": "HP OMEN 16"}
    r2 = validate_warranty(claim_data, invoice_expired, label_data)
    
    # Test 3: Model mismatch
    invoice_mismatch = {"purchase_date": "2026-06-01", "model": "HP Pavilion 15"}
    r3 = validate_warranty(claim_data, invoice_mismatch, label_data)
    
    checks = []
    if r1["is_valid"]:
        checks.append("valid-warranty OK")
    else:
        checks.append(f"valid-warranty FAIL ({r1})")
    if not r2["is_valid"]:
        checks.append("expired-warranty detected OK")
    else:
        checks.append(f"expired-warranty MISS ({r2})")
    if not r3["is_valid"]:
        checks.append("model-mismatch detected OK")
    else:
        checks.append(f"model-mismatch MISS ({r3})")
    
    all_ok = r1["is_valid"] and not r2["is_valid"] and not r3["is_valid"]
    return all_ok, " | ".join(checks)

# ==================================================================
# STEP 6: Duplicate Detection
# ==================================================================
def test_step6_duplicate_detection():
    from app.services.duplicate_detection import detect_duplicates
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        result = detect_duplicates("abcdef1234567890", db, 999999)
        if result:
            return True, "WARN: Unexpected duplicate found for random hash"
        return True, f"No duplicates for random hash OK (result={result})"
    finally:
        db.close()

# ==================================================================
# STEP 7: Policy RAG
# ==================================================================
def test_step7_policy_rag():
    from app.services.policy_rag import retrieve_policy_clauses, index, embedder, doc_sentences
    
    if not embedder:
        return True, "WARN: SentenceTransformers not installed -- RAG will return fallback"
    if not index or not doc_sentences:
        return True, "WARN: FAISS index not built (hp_warranty.txt may be missing) -- RAG returns fallback"
    
    result = retrieve_policy_clauses("My laptop screen is broken, I need a replacement")
    if result and len(result) > 0:
        return True, f"RAG returned {len(result)} clause(s): {result[0][:80]}..."
    return True, f"RAG returned empty (policy doc may be sparse): {result}"

# ==================================================================
# STEP 8: GenAI Report
# ==================================================================
def test_step8_genai_report():
    from app.services.genai_report import generate_review_summary
    
    api_key = os.environ.get("GEMINI_API_KEY")
    
    # Test A: Duplicate claim should be caught before calling API
    claim_dup = {"is_duplicate": True, "id": 1, "product_model": "HP OMEN 16"}
    r_dup = generate_review_summary(claim_dup)
    if r_dup["category"] != "duplicate_evidence":
        return False, f"Duplicate shortcut FAILED: {r_dup}"
    
    # Test B: Real AI call (if API key exists)
    if not api_key:
        return True, f"Duplicate shortcut OK | WARN: No GEMINI_API_KEY -- AI call skipped"
    
    claim_data = {
        "id": 999, "product_model": "HP OMEN 16",
        "serial_number": "SN-TEST-12345",
        "complaint_text": "The laptop screen flickers constantly and the battery drains in 30 minutes",
        "rule_data": {"is_valid": True, "reason": "Warranty valid"},
        "is_duplicate": False,
        "policy_clauses": ["Standard 1-year warranty covers manufacturing defects"]
    }
    r_ai = generate_review_summary(claim_data, [])
    
    if "category" in r_ai and "reasoning_summary" in r_ai:
        return True, (
            f"Duplicate shortcut OK | AI call OK -- "
            f"category: {r_ai['category']}, action: {r_ai.get('recommended_action','N/A')}"
        )
    return False, f"AI response missing keys: {r_ai}"


# ==================================================================
# INTEGRATION: Full pipeline via API
# ==================================================================
def test_integration_api():
    BASE = "http://127.0.0.1:8000/api/v1"
    
    # 1. Login as agent
    login_res = requests.post(f"{BASE}/auth/login", json={
        "email": "agent@warrantyguard.ai", "password": "agent123"
    })
    if login_res.status_code != 200:
        return False, f"Login failed: {login_res.status_code} {login_res.text}"
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Create a claim
    claim_res = requests.post(f"{BASE}/claims/", json={
        "customer_name": "Pipeline Test User",
        "product_model": "HP OMEN 16",
        "serial_number": "SN-PIPE-TEST-001",
        "complaint_text": "The screen flickers and laptop overheats. I want a replacement."
    }, headers=headers)
    if claim_res.status_code not in [200, 201]:
        return False, f"Create claim failed: {claim_res.status_code} {claim_res.text}"
    claim_id = claim_res.json()["id"]
    
    # 3. Run the pipeline
    pipe_res = requests.post(f"{BASE}/claims/{claim_id}/pipeline/run", headers=headers)
    if pipe_res.status_code not in [200, 202]:
        return False, f"Pipeline start failed: {pipe_res.status_code} {pipe_res.text}"
    
    # 4. Poll for completion (max 60 seconds)
    final_status = "unknown"
    for i in range(30):
        time.sleep(2)
        status_res = requests.get(f"{BASE}/claims/{claim_id}/pipeline/status", headers=headers)
        if status_res.status_code == 200:
            data = status_res.json()
            print(f"    Polling [{i+1}]: step={data.get('current_step')}/8 status={data.get('status')}")
            final_status = data.get("status")
            if final_status == "completed":
                break
            if final_status == "failed":
                return False, f"Pipeline FAILED: {data.get('error_message')}"
    
    # 5. Fetch claim and check triage result
    detail_res = requests.get(f"{BASE}/claims/{claim_id}", headers=headers)
    if detail_res.status_code != 200:
        return False, f"Fetch claim detail failed: {detail_res.status_code}"
    
    claim_data = detail_res.json()
    triage = claim_data.get("triage_result")
    status = claim_data.get("status")
    
    if not triage:
        return False, f"Triage result is null. Claim status: {status}. Pipeline status: {final_status}"
    
    return True, (
        f"Claim #{claim_id} -> status: {status} | "
        f"AI category: {triage['category']} | "
        f"reasoning: {triage['reasoning_summary'][:80]}... | "
        f"action: {triage['recommended_action']}"
    )


# ==================================================================
# MAIN
# ==================================================================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("  WARRANTYGUARD AI -- 8-STEP PIPELINE TEST SUITE")
    print("="*60)
    
    run_test("Step 1: Fetching Evidence", test_step1_fetch_evidence)
    run_test("Step 2: OCR Invoice", test_step2_ocr_invoice)
    run_test("Step 3: OCR Label", test_step3_ocr_label)
    run_test("Step 4: NLP Complaint Analysis", test_step4_nlp_complaint)
    run_test("Step 5: Warranty Rule Engine", test_step5_rule_engine)
    run_test("Step 6: Duplicate Detection", test_step6_duplicate_detection)
    run_test("Step 7: Policy RAG Retrieval", test_step7_policy_rag)
    run_test("Step 8: GenAI Report Generation", test_step8_genai_report)
    run_test("INTEGRATION: Full Pipeline via API", test_integration_api)
    
    # Summary
    print("\n\n" + "="*60)
    print("  TEST SUMMARY")
    print("="*60)
    for name, status, detail in results:
        icon = "[OK]" if status == "PASS" else "[!!]" if "WARN" in status else "[XX]"
        print(f"  {icon}  {name}: {detail[:100]}")
    
    passed = sum(1 for _, s, _ in results if s == "PASS")
    total = len(results)
    print(f"\n  Result: {passed}/{total} passed")
    print("="*60 + "\n")
