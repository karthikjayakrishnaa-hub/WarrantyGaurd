import os
import sys
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.organization import Organization
from app.models.product import Product
from app.models.user import User, UserRole
from app.models.claim import Claim
from app.models.evidence import Evidence
from app.models.triage_result import TriageResult
from app.models.audit_log import AuditLog
from app.models.warranty_policy import WarrantyPolicy
from app.models.comment import Comment
from app.models.invitation import Invitation

def seed_db():
    db = SessionLocal()
    
    # 1. Create Organization: HP
    org = db.query(Organization).filter(Organization.slug == "hp").first()
    if not org:
        org = Organization(name="Hewlett-Packard", slug="hp")
        db.add(org)
        db.commit()
        db.refresh(org)
        print(f"Created organization: {org.name}")
    else:
        print(f"Organization already exists: {org.name}")

    # 2. Add Laptops from multiple brands
    laptops = [
        # HP
        {"name": "HP Spectre x360 14", "brand": "HP", "category": "Laptop", "warranty_months": 12},
        {"name": "HP Spectre x360 16", "brand": "HP", "category": "Laptop", "warranty_months": 12},
        {"name": "HP Envy x360 15", "brand": "HP", "category": "Laptop", "warranty_months": 12},
        {"name": "HP Envy 16", "brand": "HP", "category": "Laptop", "warranty_months": 12},
        {"name": "HP Envy 17", "brand": "HP", "category": "Laptop", "warranty_months": 12},
        {"name": "HP Pavilion 14", "brand": "HP", "category": "Laptop", "warranty_months": 12},
        {"name": "HP Pavilion 15", "brand": "HP", "category": "Laptop", "warranty_months": 12},
        {"name": "HP Pavilion Plus 14", "brand": "HP", "category": "Laptop", "warranty_months": 12},
        {"name": "HP Pavilion x360", "brand": "HP", "category": "Laptop", "warranty_months": 12},
        {"name": "HP Laptop 14", "brand": "HP", "category": "Laptop", "warranty_months": 12},
        {"name": "HP Laptop 15", "brand": "HP", "category": "Laptop", "warranty_months": 12},
        {"name": "HP Laptop 17", "brand": "HP", "category": "Laptop", "warranty_months": 12},
        {"name": "HP OmniBook X 14", "brand": "HP", "category": "Laptop", "warranty_months": 12},
        {"name": "HP OMEN 16", "brand": "HP", "category": "Laptop", "warranty_months": 12},
        {"name": "HP OMEN 17", "brand": "HP", "category": "Laptop", "warranty_months": 12},
        {"name": "HP OMEN Transcend 14", "brand": "HP", "category": "Laptop", "warranty_months": 12},
        {"name": "HP OMEN Transcend 16", "brand": "HP", "category": "Laptop", "warranty_months": 12},
        {"name": "HP Victus 15", "brand": "HP", "category": "Laptop", "warranty_months": 12},
        {"name": "HP Victus 16", "brand": "HP", "category": "Laptop", "warranty_months": 12},
        {"name": "HP EliteBook 840 G10", "brand": "HP", "category": "Laptop", "warranty_months": 36},
        {"name": "HP EliteBook 845 G10", "brand": "HP", "category": "Laptop", "warranty_months": 36},
        {"name": "HP EliteBook 860 G10", "brand": "HP", "category": "Laptop", "warranty_months": 36},
        {"name": "HP EliteBook 865 G10", "brand": "HP", "category": "Laptop", "warranty_months": 36},
        {"name": "HP EliteBook 1040 G10", "brand": "HP", "category": "Laptop", "warranty_months": 36},
        {"name": "HP Elite Dragonfly G4", "brand": "HP", "category": "Laptop", "warranty_months": 36},
        {"name": "HP ProBook 440 G10", "brand": "HP", "category": "Laptop", "warranty_months": 12},
        {"name": "HP ProBook 450 G10", "brand": "HP", "category": "Laptop", "warranty_months": 12},
        {"name": "HP ZBook Firefly 14 G10", "brand": "HP", "category": "Laptop", "warranty_months": 36},
        {"name": "HP ZBook Firefly 16 G10", "brand": "HP", "category": "Laptop", "warranty_months": 36},
        {"name": "HP ZBook Power G10", "brand": "HP", "category": "Laptop", "warranty_months": 36},
        {"name": "HP ZBook Studio G10", "brand": "HP", "category": "Laptop", "warranty_months": 36},
        {"name": "HP ZBook Fury 16 G10", "brand": "HP", "category": "Laptop", "warranty_months": 36},
        {"name": "HP Chromebook 14", "brand": "HP", "category": "Laptop", "warranty_months": 12},
        {"name": "HP Chromebook x360", "brand": "HP", "category": "Laptop", "warranty_months": 12},
        {"name": "HP Elite c1030 Chromebook", "brand": "HP", "category": "Laptop", "warranty_months": 36},

        # Dell
        {"name": "Dell XPS 13", "brand": "Dell", "category": "Laptop", "warranty_months": 12},
        {"name": "Dell XPS 14", "brand": "Dell", "category": "Laptop", "warranty_months": 12},
        {"name": "Dell XPS 16", "brand": "Dell", "category": "Laptop", "warranty_months": 12},
        {"name": "Dell Inspiron 14", "brand": "Dell", "category": "Laptop", "warranty_months": 12},
        {"name": "Dell Inspiron 15", "brand": "Dell", "category": "Laptop", "warranty_months": 12},
        {"name": "Dell Inspiron 16", "brand": "Dell", "category": "Laptop", "warranty_months": 12},
        {"name": "Dell Latitude 5440", "brand": "Dell", "category": "Laptop", "warranty_months": 36},
        {"name": "Dell Latitude 7440", "brand": "Dell", "category": "Laptop", "warranty_months": 36},
        {"name": "Dell Latitude 9440", "brand": "Dell", "category": "Laptop", "warranty_months": 36},
        {"name": "Dell Precision 3580", "brand": "Dell", "category": "Laptop", "warranty_months": 36},
        {"name": "Dell Precision 5480", "brand": "Dell", "category": "Laptop", "warranty_months": 36},
        {"name": "Dell Alienware m16", "brand": "Dell", "category": "Laptop", "warranty_months": 12},
        {"name": "Dell Alienware m18", "brand": "Dell", "category": "Laptop", "warranty_months": 12},
        {"name": "Dell Alienware x14", "brand": "Dell", "category": "Laptop", "warranty_months": 12},
        {"name": "Dell Alienware x16", "brand": "Dell", "category": "Laptop", "warranty_months": 12},
        {"name": "Dell G15 Gaming", "brand": "Dell", "category": "Laptop", "warranty_months": 12},
        {"name": "Dell G16 Gaming", "brand": "Dell", "category": "Laptop", "warranty_months": 12},

        # Lenovo
        {"name": "Lenovo ThinkPad X1 Carbon", "brand": "Lenovo", "category": "Laptop", "warranty_months": 36},
        {"name": "Lenovo ThinkPad X1 Yoga", "brand": "Lenovo", "category": "Laptop", "warranty_months": 36},
        {"name": "Lenovo ThinkPad T14", "brand": "Lenovo", "category": "Laptop", "warranty_months": 36},
        {"name": "Lenovo ThinkPad E14", "brand": "Lenovo", "category": "Laptop", "warranty_months": 12},
        {"name": "Lenovo ThinkPad P1", "brand": "Lenovo", "category": "Laptop", "warranty_months": 36},
        {"name": "Lenovo Yoga 9i", "brand": "Lenovo", "category": "Laptop", "warranty_months": 12},
        {"name": "Lenovo Yoga 7i", "brand": "Lenovo", "category": "Laptop", "warranty_months": 12},
        {"name": "Lenovo Yoga Pro 9i", "brand": "Lenovo", "category": "Laptop", "warranty_months": 12},
        {"name": "Lenovo IdeaPad Slim 5", "brand": "Lenovo", "category": "Laptop", "warranty_months": 12},
        {"name": "Lenovo IdeaPad Slim 3", "brand": "Lenovo", "category": "Laptop", "warranty_months": 12},
        {"name": "Lenovo Legion Pro 7i", "brand": "Lenovo", "category": "Laptop", "warranty_months": 12},
        {"name": "Lenovo Legion Pro 5i", "brand": "Lenovo", "category": "Laptop", "warranty_months": 12},
        {"name": "Lenovo Legion Slim 7i", "brand": "Lenovo", "category": "Laptop", "warranty_months": 12},
        {"name": "Lenovo LOQ 15", "brand": "Lenovo", "category": "Laptop", "warranty_months": 12},

        # Asus
        {"name": "Asus Zenbook 14 OLED", "brand": "Asus", "category": "Laptop", "warranty_months": 12},
        {"name": "Asus Zenbook Pro 16X OLED", "brand": "Asus", "category": "Laptop", "warranty_months": 12},
        {"name": "Asus Zenbook Duo", "brand": "Asus", "category": "Laptop", "warranty_months": 12},
        {"name": "Asus Vivobook 15", "brand": "Asus", "category": "Laptop", "warranty_months": 12},
        {"name": "Asus Vivobook 16", "brand": "Asus", "category": "Laptop", "warranty_months": 12},
        {"name": "Asus Vivobook Pro 15 OLED", "brand": "Asus", "category": "Laptop", "warranty_months": 12},
        {"name": "Asus ROG Zephyrus G14", "brand": "Asus", "category": "Laptop", "warranty_months": 12},
        {"name": "Asus ROG Zephyrus G16", "brand": "Asus", "category": "Laptop", "warranty_months": 12},
        {"name": "Asus ROG Strix SCAR 16", "brand": "Asus", "category": "Laptop", "warranty_months": 12},
        {"name": "Asus ROG Strix SCAR 18", "brand": "Asus", "category": "Laptop", "warranty_months": 12},
        {"name": "Asus TUF Gaming A15", "brand": "Asus", "category": "Laptop", "warranty_months": 12},
        {"name": "Asus TUF Gaming F15", "brand": "Asus", "category": "Laptop", "warranty_months": 12},
        {"name": "Asus ExpertBook B9", "brand": "Asus", "category": "Laptop", "warranty_months": 36},

        # MSI
        {"name": "MSI Titan 18 HX", "brand": "MSI", "category": "Laptop", "warranty_months": 12},
        {"name": "MSI Raider GE78", "brand": "MSI", "category": "Laptop", "warranty_months": 12},
        {"name": "MSI Vector 16 HX", "brand": "MSI", "category": "Laptop", "warranty_months": 12},
        {"name": "MSI Stealth 16", "brand": "MSI", "category": "Laptop", "warranty_months": 12},
        {"name": "MSI Stealth 14", "brand": "MSI", "category": "Laptop", "warranty_months": 12},
        {"name": "MSI Pulse 15", "brand": "MSI", "category": "Laptop", "warranty_months": 12},
        {"name": "MSI Katana 15", "brand": "MSI", "category": "Laptop", "warranty_months": 12},
        {"name": "MSI Cyborg 15", "brand": "MSI", "category": "Laptop", "warranty_months": 12},
        {"name": "MSI Prestige 16", "brand": "MSI", "category": "Laptop", "warranty_months": 12},
        {"name": "MSI Summit E16", "brand": "MSI", "category": "Laptop", "warranty_months": 12},
        {"name": "MSI Modern 15", "brand": "MSI", "category": "Laptop", "warranty_months": 12},

        # Apple
        {"name": "Apple MacBook Air 13 (M2)", "brand": "Apple", "category": "Laptop", "warranty_months": 12},
        {"name": "Apple MacBook Air 13 (M3)", "brand": "Apple", "category": "Laptop", "warranty_months": 12},
        {"name": "Apple MacBook Air 15 (M3)", "brand": "Apple", "category": "Laptop", "warranty_months": 12},
        {"name": "Apple MacBook Pro 14 (M3)", "brand": "Apple", "category": "Laptop", "warranty_months": 12},
        {"name": "Apple MacBook Pro 14 (M3 Pro)", "brand": "Apple", "category": "Laptop", "warranty_months": 12},
        {"name": "Apple MacBook Pro 16 (M3 Max)", "brand": "Apple", "category": "Laptop", "warranty_months": 12},

        # Acer
        {"name": "Acer Swift 3", "brand": "Acer", "category": "Laptop", "warranty_months": 12},
        {"name": "Acer Swift 14", "brand": "Acer", "category": "Laptop", "warranty_months": 12},
        {"name": "Acer Swift X", "brand": "Acer", "category": "Laptop", "warranty_months": 12},
        {"name": "Acer Aspire 5", "brand": "Acer", "category": "Laptop", "warranty_months": 12},
        {"name": "Acer Aspire 3", "brand": "Acer", "category": "Laptop", "warranty_months": 12},
        {"name": "Acer Predator Helios 16", "brand": "Acer", "category": "Laptop", "warranty_months": 12},
        {"name": "Acer Predator Helios 18", "brand": "Acer", "category": "Laptop", "warranty_months": 12},
        {"name": "Acer Nitro 5", "brand": "Acer", "category": "Laptop", "warranty_months": 12},
        {"name": "Acer Nitro 16", "brand": "Acer", "category": "Laptop", "warranty_months": 12},
        {"name": "Acer Chromebook Spin 714", "brand": "Acer", "category": "Laptop", "warranty_months": 12}
    ]

    for lap in laptops:
        prod = db.query(Product).filter(Product.name == lap["name"], Product.org_id == org.id).first()
        if not prod:
            prod = Product(**lap, org_id=org.id)
            db.add(prod)
            print(f"Added product: {prod.name}")

    from app.core.security import hash_password

    # 3. Add Demo Admin
    admin = db.query(User).filter(User.email == "admin@warrantyguard.ai").first()
    if not admin:
        admin = User(
            email="admin@warrantyguard.ai", 
            hashed_password=hash_password("admin123"), 
            full_name="Demo Admin", 
            role=UserRole.admin,
            org_id=org.id
        )
        db.add(admin)
        print("Created Demo Admin user")

    # 4. Add Demo Agent
    agent = db.query(User).filter(User.email == "agent@warrantyguard.ai").first()
    if not agent:
        agent = User(
            email="agent@warrantyguard.ai", 
            hashed_password=hash_password("agent123"), 
            full_name="Demo Agent", 
            role=UserRole.agent,
            org_id=org.id
        )
        db.add(agent)
        print("Created Demo Agent user")

    db.commit()
    db.close()

if __name__ == "__main__":
    seed_db()
