from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.types import Uuid as UUID
from sqlalchemy.orm import relationship

from app.core.database import Base

class WarrantyPolicy(Base):
    __tablename__ = "warranty_policies"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    file_path = Column(String, nullable=False)
    version = Column(String, default="1.0")
    is_active = Column(Boolean, default=True)

    # Relationships
    organization = relationship("Organization", back_populates="policies")
    product = relationship("Product", back_populates="policies")
