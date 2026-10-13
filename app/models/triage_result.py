from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.types import Uuid as UUID
from sqlalchemy.orm import relationship

from app.core.database import Base

class TriageCategory(str, Enum):
    approved = "approved"
    expired_warranty = "expired_warranty"
    identity_mismatch = "identity_mismatch"
    duplicate_evidence = "duplicate_evidence"
    needs_manual_review = "needs_manual_review"
    policy_exception = "policy_exception"
    rejected = "rejected"

class TriageResult(Base):
    __tablename__ = "triage_results"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)
    claim_id = Column(Integer, ForeignKey("claims.id"), unique=True)
    category = Column(SQLEnum(TriageCategory))
    reasoning_summary = Column(Text)
    recommended_action = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    claim = relationship("Claim", back_populates="triage_result")
