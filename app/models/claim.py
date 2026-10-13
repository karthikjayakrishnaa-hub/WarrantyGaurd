from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.types import Uuid as UUID
from sqlalchemy.orm import relationship

from app.core.database import Base

class ClaimStatus(str, Enum):
    submitted = "submitted"
    processing = "processing"
    triaged = "triaged"
    approved = "approved"
    rejected = "rejected"
    closed = "closed"

class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True) # Nullable for legacy
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_agent_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    customer_name = Column(String, index=True)
    product_model = Column(String, index=True)
    serial_number = Column(String, index=True)
    complaint_text = Column(Text)
    status = Column(SQLEnum(ClaimStatus), default=ClaimStatus.submitted)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", foreign_keys=[user_id], back_populates="claims")
    assigned_agent = relationship("User", foreign_keys=[assigned_agent_id])
    organization = relationship("Organization", back_populates="claims")
    evidence = relationship("Evidence", back_populates="claim")
    triage_result = relationship("TriageResult", back_populates="claim", uselist=False)
    audit_logs = relationship("AuditLog", back_populates="claim", order_by="AuditLog.created_at.desc()")
    comments = relationship("Comment", back_populates="claim", cascade="all, delete-orphan")
