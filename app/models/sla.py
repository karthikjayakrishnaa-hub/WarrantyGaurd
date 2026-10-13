from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Uuid as UUID
from app.core.database import Base

class SLA(Base):
    __tablename__ = "slas"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, unique=True)
    response_target_hours = Column(Integer, default=24)
    resolution_target_hours = Column(Integer, default=72)

    org = relationship("Organization")