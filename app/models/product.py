from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.types import Uuid as UUID
from sqlalchemy.orm import relationship

from app.core.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    
    name = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    category = Column(String, nullable=False)
    warranty_months = Column(Integer, default=12)

    # Relationships
    organization = relationship("Organization", back_populates="products")
    policies = relationship("WarrantyPolicy", back_populates="product")
