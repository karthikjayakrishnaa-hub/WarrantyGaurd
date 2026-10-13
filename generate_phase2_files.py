import os

SCHEMA_CODE = {
    "app/schemas/organization.py": """
from typing import Optional, Any
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class OrganizationBase(BaseModel):
    name: str
    slug: str
    is_active: bool = True

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationResponse(OrganizationBase):
    id: UUID
    created_at: datetime
    
    model_config = {"from_attributes": True}
""",
    "app/schemas/product.py": """
from typing import Optional
from pydantic import BaseModel
from uuid import UUID

class ProductBase(BaseModel):
    name: str
    brand: str
    category: str
    warranty_months: int = 12

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    org_id: UUID
    
    model_config = {"from_attributes": True}
""",
    "app/schemas/comment.py": """
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class CommentBase(BaseModel):
    body: str
    is_internal: bool = False

class CommentCreate(CommentBase):
    claim_id: int

class CommentResponse(CommentBase):
    id: int
    claim_id: int
    user_id: int
    created_at: datetime
    
    model_config = {"from_attributes": True}
""",
    "app/schemas/invitation.py": """
from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID
from app.models.user import UserRole

class InvitationBase(BaseModel):
    email: EmailStr
    role: UserRole

class InvitationCreate(InvitationBase):
    pass

class InvitationResponse(InvitationBase):
    id: int
    org_id: UUID
    expires_at: datetime
    accepted_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}
""",
    "app/schemas/warranty_policy.py": """
from typing import Optional
from pydantic import BaseModel
from uuid import UUID

class WarrantyPolicyBase(BaseModel):
    product_id: int
    file_path: str
    version: str = "1.0"
    is_active: bool = True

class WarrantyPolicyCreate(WarrantyPolicyBase):
    pass

class WarrantyPolicyResponse(WarrantyPolicyBase):
    id: int
    org_id: UUID
    
    model_config = {"from_attributes": True}
"""
}

ROUTER_CODE = {
    "app/api/v1/endpoints/organizations.py": """
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user, require_org, require_role
from app.models.organization import Organization
from app.schemas.organization import OrganizationResponse, OrganizationCreate

router = APIRouter()

@router.get("/me", response_model=OrganizationResponse)
def get_my_organization(db: Session = Depends(get_db), current_user = Depends(require_org)):
    org = db.query(Organization).filter(Organization.id == current_user.org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org
""",
    "app/api/v1/endpoints/products.py": """
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user, require_org, require_role
from app.models.product import Product
from app.schemas.product import ProductResponse, ProductCreate

router = APIRouter()

@router.get("/", response_model=List[ProductResponse])
def list_products(db: Session = Depends(get_db), current_user = Depends(require_org)):
    return db.query(Product).filter(Product.org_id == current_user.org_id).all()

@router.post("/", response_model=ProductResponse, dependencies=[Depends(require_role(["admin", "super_admin"]))])
def create_product(product_in: ProductCreate, db: Session = Depends(get_db), current_user = Depends(require_org)):
    product = Product(**product_in.model_dump(), org_id=current_user.org_id)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product
""",
    "app/api/v1/endpoints/comments.py": """
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user, require_org
from app.models.comment import Comment
from app.models.claim import Claim
from app.models.user import UserRole
from app.schemas.comment import CommentResponse, CommentCreate

router = APIRouter()

@router.get("/claim/{claim_id}", response_model=List[CommentResponse])
def get_claim_comments(claim_id: int, db: Session = Depends(get_db), current_user = Depends(require_org)):
    claim = db.query(Claim).filter(Claim.id == claim_id, Claim.org_id == current_user.org_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
        
    query = db.query(Comment).filter(Comment.claim_id == claim_id)
    if current_user.role == UserRole.customer:
        query = query.filter(Comment.is_internal == False)
    return query.all()

@router.post("/", response_model=CommentResponse)
def add_comment(comment_in: CommentCreate, db: Session = Depends(get_db), current_user = Depends(require_org)):
    claim = db.query(Claim).filter(Claim.id == comment_in.claim_id, Claim.org_id == current_user.org_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
        
    if current_user.role == UserRole.customer and comment_in.is_internal:
        raise HTTPException(status_code=403, detail="Customers cannot add internal comments")
        
    comment = Comment(**comment_in.model_dump(), user_id=current_user.id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment
""",
    "app/api/v1/endpoints/invitations.py": """
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import secrets
from datetime import datetime, timedelta, timezone
from app.core.database import get_db
from app.core.security import require_org, require_role
from app.models.invitation import Invitation
from app.schemas.invitation import InvitationResponse, InvitationCreate

router = APIRouter()

@router.post("/", response_model=InvitationResponse, dependencies=[Depends(require_role(["admin", "super_admin"]))])
def create_invitation(inv_in: InvitationCreate, db: Session = Depends(get_db), current_user = Depends(require_org)):
    inv = Invitation(
        **inv_in.model_dump(),
        org_id=current_user.org_id,
        token=secrets.token_urlsafe(32),
        expires_at=datetime.now(timezone.utc) + timedelta(days=7)
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv
""",
    "app/api/v1/endpoints/policies.py": """
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import require_org, require_role
from app.models.warranty_policy import WarrantyPolicy
from app.schemas.warranty_policy import WarrantyPolicyResponse, WarrantyPolicyCreate

router = APIRouter()

@router.get("/", response_model=List[WarrantyPolicyResponse])
def list_policies(db: Session = Depends(get_db), current_user = Depends(require_org)):
    return db.query(WarrantyPolicy).filter(WarrantyPolicy.org_id == current_user.org_id).all()
"""
}

for path, content in {**SCHEMA_CODE, **ROUTER_CODE}.items():
    with open(path, "w") as f:
        f.write(content.strip() + "\\n")

print("Files generated.")
