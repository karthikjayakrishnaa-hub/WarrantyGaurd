from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class PipelineStatus(Base):
    __tablename__ = "pipeline_statuses"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, ForeignKey("claims.id"), nullable=False, unique=True)
    current_step = Column(Integer, default=0)
    total_steps = Column(Integer, default=8)
    status = Column(String, default="pending") # pending, running, completed, failed
    error_message = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    claim = relationship("Claim")