import imagehash
from sqlalchemy.orm import Session
from app.models.evidence import Evidence
from app.models.claim import Claim, ClaimStatus

# Only treat claims that completed submission as real evidence sources.
# This prevents orphaned "ghost" claims (from partial failed submissions)
# from being used as duplicate references.
_REAL_CLAIM_STATUSES = [
    ClaimStatus.submitted,
    ClaimStatus.triaged,
    ClaimStatus.approved,
    ClaimStatus.rejected,
    ClaimStatus.closed,
]

# Strict threshold: 2 bits difference out of 64 (~97% similarity).
# Threshold of 5 was too loose and caused false positives on visually
# different products photographed against similar backgrounds.
_PHASH_THRESHOLD = 2


def detect_duplicates(phash: str, db: Session, current_claim_id: int, org_id=None) -> bool:
    if not phash:
        return False

    # Get the org of the current claim for scoping
    current_claim = db.query(Claim).filter(Claim.id == current_claim_id).first()
    scope_org_id = org_id or (current_claim.org_id if current_claim else None)

    # Build query: only compare against real completed claims within the same org.
    query = (
        db.query(Evidence)
        .join(Claim, Claim.id == Evidence.claim_id)
        .filter(
            Evidence.phash.isnot(None),
            Evidence.claim_id != current_claim_id,
            Claim.status.in_(_REAL_CLAIM_STATUSES),
        )
    )

    # Scope to same organisation if available (prevent cross-tenant false positives)
    if scope_org_id:
        query = query.filter(Claim.org_id == scope_org_id)

    existing_evidence = query.all()

    try:
        current_hash = imagehash.hex_to_hash(phash)
        for ev in existing_evidence:
            if ev.phash:
                ev_hash = imagehash.hex_to_hash(ev.phash)
                if current_hash - ev_hash <= _PHASH_THRESHOLD:
                    return True
    except Exception as e:
        print(f"Error in duplicate detection: {e}")
        return False

    return False
