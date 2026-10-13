import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.types import Uuid as UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.user import UserRole

class Invitation(Base):
    __tablename__ = "invitations"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    
    email = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.agent)
    token = Column(String, unique=True, default=lambda: str(uuid.uuid4()))
    
    expires_at = Column(DateTime, nullable=False)
    accepted_at = Column(DateTime, nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="invitations")
