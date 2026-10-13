from fastapi import APIRouter

from app.api.v1.endpoints import health, claims, evidence, pipeline, auth, organizations, products, comments, invitations, policies, sse, sla, stats

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(claims.router, prefix="/claims", tags=["claims"])
api_router.include_router(evidence.router, prefix="/claims", tags=["evidence"])
api_router.include_router(pipeline.router, prefix="/claims", tags=["pipeline"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(comments.router, prefix="/comments", tags=["comments"])
api_router.include_router(invitations.router, prefix="/invitations", tags=["invitations"])
api_router.include_router(policies.router, prefix="/policies", tags=["policies"])
api_router.include_router(sse.router, prefix="/sse", tags=["sse"])
api_router.include_router(sla.router, prefix="/sla", tags=["sla"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])
