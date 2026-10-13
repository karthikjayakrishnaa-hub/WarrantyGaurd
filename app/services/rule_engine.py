from datetime import datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session
from app.models.product import Product

def validate_warranty(db: Session, claim_data: dict, invoice_data: dict, label_data: dict) -> dict:
    is_valid = True
    reasons = []

    claimed_model = claim_data.get("product_model")
    
    # Fetch original product details from DB
    product = db.query(Product).filter(Product.name.ilike(f"%{claimed_model}%")).first() if claimed_model else None
    warranty_months = product.warranty_months if product else 12

    # 1. Check purchase date
    purchase_date_str = invoice_data.get("purchase_date")
    if purchase_date_str:
        try:
            purchase_date = datetime.strptime(purchase_date_str, "%Y-%m-%d")
            warranty_end = purchase_date + relativedelta(months=warranty_months)
            if datetime.now() > warranty_end:
                is_valid = False
                reasons.append(f"Warranty expired (Allowed: {warranty_months} months)")
        except ValueError:
            reasons.append("Invalid purchase date format")
    else:
        reasons.append("No purchase date found")

    # 2. Check model mismatch
    claimed_model = claim_data.get("product_model")
    invoice_model = invoice_data.get("model")
    label_model = label_data.get("model")

    if invoice_model and invoice_model != claimed_model:
        is_valid = False
        reasons.append(f"Invoice model ({invoice_model}) does not match claimed model ({claimed_model})")
    
    if label_model and label_model != claimed_model:
        is_valid = False
        reasons.append(f"Label model ({label_model}) does not match claimed model ({claimed_model})")

    return {
        "is_valid": is_valid,
        "reason": ", ".join(reasons) if reasons else "Warranty valid"
    }
