import os
import sys
import secrets
import string

# Ensure the app directory is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.models.organization import Organization
from app.models.claim import Claim
from app.models.product import Product
from app.models.evidence import Evidence
from app.models.triage_result import TriageResult
from app.models.audit_log import AuditLog
from app.models.warranty_policy import WarrantyPolicy
from app.models.comment import Comment
from app.models.invitation import Invitation

def generate_secure_password(length=12):
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(characters) for _ in range(length))

def create_credentials():
    db = SessionLocal()
    
    # Ensure HP org exists
    org = db.query(Organization).filter(Organization.slug == "hp").first()
    if not org:
        org = Organization(name="Hewlett-Packard", slug="hp")
        db.add(org)
        db.commit()
        db.refresh(org)

    # Generate secure passwords
    admin_password = generate_secure_password()
    customer_password = generate_secure_password()

    # Create Admin
    admin_email = "admin_live@hp.com"
    admin = db.query(User).filter(User.email == admin_email).first()
    if not admin:
        admin = User(
            email=admin_email,
            hashed_password=hash_password(admin_password),
            full_name="Live Admin",
            role=UserRole.admin,
            org_id=org.id,
            is_active=True
        )
        db.add(admin)
    else:
        admin.hashed_password = hash_password(admin_password) # Reset password
    
    # Create Customer
    customer_email = "customer_live@example.com"
    customer = db.query(User).filter(User.email == customer_email).first()
    if not customer:
        customer = User(
            email=customer_email,
            hashed_password=hash_password(customer_password),
            full_name="Live Customer",
            role=UserRole.customer,
            org_id=org.id,
            is_active=True
        )
        db.add(customer)
    else:
         customer.hashed_password = hash_password(customer_password) # Reset password

    db.commit()
    db.close()

    print("\n" + "="*40)
    print("      LIVE CREDENTIALS GENERATED      ")
    print("="*40)
    print("\n[Admin Account]")
    print(f"Email:    {admin_email}")
    print(f"Password: {admin_password}")
    print("Role:     Admin (Can access Admin Panel, Analytics, Bulk Ops)")
    
    print("\n[Customer Account]")
    print(f"Email:    {customer_email}")
    print(f"Password: {customer_password}")
    print("Role:     Customer (Can access Customer Portal, Submit Claims)")
    print("\n" + "="*40 + "\n")

if __name__ == "__main__":
    create_credentials()
