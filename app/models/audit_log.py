from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.types import Uuid as UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class AuditAction(str, Enum):
    claim_created = "claim_created"
    evidence_uploaded = "evidence_uploaded"
    pipeline_started = "pipeline_started"
    pipeline_completed = "pipeline_completed"
    status_changed = "status_changed"
    claim_approved = "claim_approved"
    claim_rejected = "claim_rejected"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)
    claim_id = Column(Integer, ForeignKey("claims.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(SQLEnum(AuditAction), nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    claim = relationship("Claim", back_populates="audit_logs")
    user = relationship("User", back_populates="audit_logs")
