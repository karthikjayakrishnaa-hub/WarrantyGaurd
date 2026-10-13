import os

MODELS_CODE = {
    "app/models/refresh_token.py": """
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
"""
}

CORE_CODE = {
    "app/core/rate_limit.py": """
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded

# Global rate limiter using remote IP address
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

def setup_rate_limiting(app: FastAPI):
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
""",
    "app/core/middleware.py": """
from fastapi import Request, FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Content-Security-Policy"] = "default-src 'self'; img-src 'self' data: https:; script-src 'self'; style-src 'self' 'unsafe-inline'"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

def setup_middlewares(app: FastAPI):
    app.add_middleware(SecurityHeadersMiddleware)
""",
    "app/core/validators.py": """
import re
from fastapi import HTTPException

def validate_password(password: str) -> str:
    \"\"\"
    Enforces password policy: min 8 chars, 1 uppercase, 1 lowercase, 1 digit, 1 special character.
    \"\"\"
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain at least one lowercase letter")
    if not re.search(r"[0-9]", password):
        raise ValueError("Password must contain at least one digit")
    if not re.search(r"[!@#$%^&*(),.?\\":{}|<>]", password):
        raise ValueError("Password must contain at least one special character")
    return password

def sanitize_html(text: str) -> str:
    \"\"\"
    Basic HTML stripping to prevent XSS.
    \"\"\"
    if not text:
        return text
    # Strip simple HTML tags
    clean_text = re.sub(r'<[^>]*>', '', text)
    return clean_text
"""
}

for path, content in {**MODELS_CODE, **CORE_CODE}.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content.strip() + "\\n")

print("Files generated.")
