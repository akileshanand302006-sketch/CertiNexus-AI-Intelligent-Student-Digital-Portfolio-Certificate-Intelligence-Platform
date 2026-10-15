"""
CertiNexus AI — Authentication API

Handles registration, login, token refresh, and JWT management.
"""

import os
from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.schemas.schemas import TokenRefresh, TokenResponse, UserLogin, UserRegister

router = APIRouter()


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    pwd_bytes = password.encode("utf-8")[:72]
    return bcrypt.hashpw(pwd_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a bcrypt hash."""
    pwd_bytes = plain_password.encode("utf-8")[:72]
    return bcrypt.checkpw(pwd_bytes, hashed_password.encode("utf-8"))

# JWT config
JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret-key-change-in-production")
JWT_REFRESH_SECRET = os.environ.get("JWT_REFRESH_SECRET", "dev-refresh-secret-change-in-production")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE = int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE = int(os.environ.get("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    to_encode["exp"] = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE)
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    to_encode["exp"] = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE)
    return jwt.encode(to_encode, JWT_REFRESH_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(lambda: None),  # Will be replaced by header extraction
) -> User:
    """Get current user from JWT token."""
    # This is handled by the dependency below
    pass


from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.repositories.user_repository import UserRepository

security = HTTPBearer()
user_repo = UserRepository()


def get_current_user_dep(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Dependency to extract current user from Bearer token."""
    payload = verify_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        # Check MongoDB repository
        mongo_user = user_repo.find_by_id(user_id)
        if mongo_user:
            # Rehydrate/sync into local SQLite session for ORM dependencies
            user = User(
                id=mongo_user.get("_id") or mongo_user.get("id"),
                email=mongo_user.get("email"),
                username=mongo_user.get("username"),
                hashed_password=mongo_user.get("password_hash", ""),
                full_name=mongo_user.get("full_name", ""),
                role=mongo_user.get("role", "student"),
                is_active=mongo_user.get("is_active", True),
            )
            try:
                db.merge(user)
                db.commit()
            except Exception:
                db.rollback()
        else:
            raise HTTPException(status_code=401, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")
    return user


@router.post("/register", response_model=TokenResponse)
async def register(data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user account in MongoDB Atlas and local session."""
    # Check existing in SQLite or MongoDB
    if db.query(User).filter(User.email == data.email).first() or user_repo.find_by_email(data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.username == data.username).first() or user_repo.find_by_username(data.username):
        raise HTTPException(status_code=400, detail="Username already taken")

    pwd_hash = hash_password(data.password)

    # 1. Create user in SQLite
    user = User(
        email=data.email,
        username=data.username,
        hashed_password=pwd_hash,
        full_name=data.full_name,
        institution=data.institution,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # 2. Persist in MongoDB Atlas
    try:
        user_repo.create({
            "_id": user.id,
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "password_hash": pwd_hash,
            "full_name": user.full_name or "",
            "institution": user.institution or "",
            "role": user.role,
            "is_active": user.is_active,
        })
    except Exception as e:
        print(f"Notice: MongoDB user persistence fallback: {e}")

    # Generate tokens
    token_data = {"sub": user.id, "email": user.email, "role": user.role}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: Session = Depends(get_db)):
    """Login with email or username and password via MongoDB Atlas / local session."""
    identifier = (data.username_or_email or data.email or data.username or "").strip()
    if not identifier:
        raise HTTPException(status_code=400, detail="Please provide your email or username")
    user = db.query(User).filter((User.email == identifier) | (User.username == identifier)).first()
    
    # Check MongoDB if not found in local SQLite
    if not user:
        mongo_user = user_repo.find_by_email(identifier) or user_repo.find_by_username(identifier)
        if mongo_user:
            user = User(
                id=mongo_user.get("_id") or mongo_user.get("id"),
                email=mongo_user.get("email"),
                username=mongo_user.get("username"),
                hashed_password=mongo_user.get("password_hash"),
                full_name=mongo_user.get("full_name"),
                institution=mongo_user.get("institution"),
                role=mongo_user.get("role", "student"),
                is_active=mongo_user.get("is_active", True),
            )
            try:
                db.merge(user)
                db.commit()
            except Exception:
                db.rollback()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")
        
    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    # Sync to MongoDB if not present
    try:
        if not user_repo.find_by_email(user.email):
            user_repo.create({
                "_id": user.id,
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "password_hash": user.hashed_password,
                "full_name": user.full_name or "",
                "institution": user.institution or "",
                "role": user.role,
                "is_active": user.is_active,
            })
    except Exception as e:
        print(f"Notice: MongoDB sync notice on login: {e}")

    token_data = {"sub": user.id, "email": user.email, "role": user.role}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: TokenRefresh, db: Session = Depends(get_db)):
    """Refresh access token using refresh token."""
    try:
        payload = jwt.decode(data.refresh_token, JWT_REFRESH_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        mongo_user = user_repo.find_by_id(user_id)
        if mongo_user:
            user = User(
                id=mongo_user.get("_id") or mongo_user.get("id"),
                email=mongo_user.get("email"),
                username=mongo_user.get("username"),
                hashed_password=mongo_user.get("password_hash", ""),
                full_name=mongo_user.get("full_name", ""),
                role=mongo_user.get("role", "student"),
                is_active=mongo_user.get("is_active", True),
            )
        else:
            raise HTTPException(status_code=401, detail="User not found")

    token_data = {"sub": user.id, "email": user.email, "role": user.role}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )
