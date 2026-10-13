from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.types import Uuid as UUID
from sqlalchemy.orm import relationship

from app.core.database import Base

class EvidenceType(str, Enum):
    invoice = "invoice"
    product_photo = "product_photo"
    label_photo = "label_photo"
    policy_doc = "policy_doc"

class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)
    claim_id = Column(Integer, ForeignKey("claims.id"))
    type = Column(SQLEnum(EvidenceType))
    file_path = Column(String)
    file_hash = Column(String)
    phash = Column(String, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    claim = relationship("Claim", back_populates="evidence")
