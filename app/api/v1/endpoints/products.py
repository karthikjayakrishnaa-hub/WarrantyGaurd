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