from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog, AuditAction


def log_action(
    db: Session,
    claim_id: int,
    action: AuditAction,
    user_id: int = None,
    details: str = None,
):
    """Create an audit log entry for a claim action."""
    entry = AuditLog(
        claim_id=claim_id,
        user_id=user_id,
        action=action,
        details=details,
    )
    db.add(entry)
    db.flush()  # flush so the entry gets an ID but don't commit yet (let the caller commit)
    return entry
