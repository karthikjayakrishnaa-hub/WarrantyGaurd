from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, get_current_user
from app.models.user import User, UserRole
from app.models.organization import Organization
from app.models.refresh_token import RefreshToken
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token, RefreshTokenRequest, PasswordChangeRequest
import secrets
from datetime import datetime, timedelta, timezone

router = APIRouter()


@router.post("/register", response_model=Token, status_code=201)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # Check if email already exists
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    if len(user_in.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters.",
        )

    # For demo purposes, assign all new registrations to HP
    default_org = db.query(Organization).filter(Organization.slug == "hp").first()
    
    user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        full_name=user_in.full_name,
        role=UserRole.customer,  # new registrations are always customers
        org_id=default_org.id if default_org else None
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create refresh token
    refresh_token = secrets.token_urlsafe(32)
    db_rt = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7)
    )
    db.add(db_rt)
    db.commit()

    token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=token, refresh_token=refresh_token, user=UserResponse.model_validate(user))


from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.core.rate_limit import limiter

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def login(request: Request, credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated.",
        )

    # Create refresh token
    refresh_token = secrets.token_urlsafe(32)
    db_rt = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7)
    )
    db.add(db_rt)
    db.commit()

    token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=token, refresh_token=refresh_token, user=UserResponse.model_validate(user))

@router.post("/refresh", response_model=Token)
def refresh_token(req: RefreshTokenRequest, db: Session = Depends(get_db)):
    rt = db.query(RefreshToken).filter(
        RefreshToken.token == req.refresh_token,
        RefreshToken.revoked == False
    ).first()

    if not rt or rt.expires_at < datetime.now(timezone.utc).replace(tzinfo=None):
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user = db.query(User).filter(User.id == rt.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User inactive or deleted")

    new_access_token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=new_access_token, refresh_token=rt.token, user=UserResponse.model_validate(user))

@router.post("/logout", status_code=200)
def logout(req: RefreshTokenRequest, db: Session = Depends(get_db)):
    rt = db.query(RefreshToken).filter(RefreshToken.token == req.refresh_token).first()
    if rt:
        rt.revoked = True
        db.commit()
    return {"message": "Logged out successfully"}

@router.post("/change-password", status_code=200)
def change_password(req: PasswordChangeRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not verify_password(req.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect old password")
        
    current_user.hashed_password = hash_password(req.new_password)
    
    # Revoke all existing refresh tokens for this user
    db.query(RefreshToken).filter(RefreshToken.user_id == current_user.id).update({"revoked": True})
    
    db.commit()
    return {"message": "Password changed successfully"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/users", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == UserRole.super_admin:
        return db.query(User).all()
    elif current_user.org_id:
        return db.query(User).filter(User.org_id == current_user.org_id).all()
    else:
        return [current_user]
