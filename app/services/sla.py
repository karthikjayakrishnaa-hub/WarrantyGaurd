from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List
from app.models.claim import Claim
from app.models.sla import SLA

def get_overdue_claims(db: Session, org_id: str) -> List[Claim]:
    sla = db.query(SLA).filter(SLA.org_id == org_id).first()
    if not sla:
        return []
    
    # In a real app, this would use a complex SQL query to calculate hours elapsed
    # For now, we mock returning claims older than the resolution target
    from datetime import timedelta
    target_date = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=sla.resolution_target_hours)
    
    overdue = db.query(Claim).filter(
        Claim.org_id == org_id,
        Claim.status != "resolved",
        Claim.created_at < target_date
    ).all()
    
    return overdue