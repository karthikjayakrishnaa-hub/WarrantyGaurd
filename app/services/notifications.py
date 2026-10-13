from sqlalchemy.orm import Session
from app.models.user import User
from app.models.claim import Claim

def send_status_change_email(db: Session, claim: Claim, new_status: str):
    # Mock sending email
    user = db.query(User).filter(User.id == claim.user_id).first()
    if user:
        print(f"[EMAIL MOCK] To: {user.email} | Subject: Claim #{claim.id} Status Updated | Body: Your claim status is now {new_status}")