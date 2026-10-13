import os
os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["FLAGS_enable_pir_api"] = "0"

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.api.v1.router import api_router
from app.core.rate_limit import setup_rate_limiting
from app.core.middleware import setup_middlewares


def seed_admin_user():
    """Create default admin and agent accounts on first run."""
    from app.models.user import User, UserRole
    from app.core.security import hash_password

    db = SessionLocal()
    try:
        # Only seed if no users exist
        if db.query(User).count() == 0:
            admin = User(
                email="admin@warrantyguard.ai",
                hashed_password=hash_password("admin123"),
                full_name="System Admin",
                role=UserRole.admin,
            )
            agent = User(
                email="agent@warrantyguard.ai",
                hashed_password=hash_password("agent123"),
                full_name="Default Agent",
                role=UserRole.agent,
            )
            db.add(admin)
            db.add(agent)
            db.commit()
            print("[OK] Seeded default admin (admin@warrantyguard.ai) and agent (agent@warrantyguard.ai) accounts")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure storage, seed
    os.makedirs(settings.STORAGE_PATH, exist_ok=True)
    # Base.metadata.create_all(bind=engine) # Handled by Alembic now
    seed_admin_user()
    yield
    # Shutdown: nothing needed


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_rate_limiting(app)
setup_middlewares(app)

app.include_router(api_router, prefix=settings.API_V1_STR)

from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description = app.description,
        routes=app.routes,
    )
    # Remove 422 response from all endpoints in Swagger UI
    for path in openapi_schema.get("paths", {}).values():
        for method in path.values():
            if "responses" in method and "422" in method["responses"]:
                del method["responses"]["422"]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.get("/health")
def health_check():
    return {"status": "ok"}
