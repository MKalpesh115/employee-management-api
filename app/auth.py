from datetime import datetime, timedelta, timezone
import os

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import TokenResponse, UserLogin, UserRegister, UserResponse

router = APIRouter(prefix="/auth", tags=["authentication"])
password_hasher = PasswordHasher()
bearer_scheme = HTTPBearer(auto_error=False)

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
MINIMUM_SECRET_LENGTH = 32


def get_secret_key() -> str:
    """Read the signing key from the environment, never from source code."""
    secret_key = os.getenv("JWT_SECRET_KEY")
    if not secret_key or len(secret_key) < MINIMUM_SECRET_LENGTH:
        raise RuntimeError(
            "Set JWT_SECRET_KEY to a randomly generated value of at least 32 characters."
        )
    return secret_key


def create_access_token(user_id: int) -> str:
    """Create a signed JWT that expires after 30 minutes."""
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return jwt.encode(
        {"sub": str(user_id), "exp": expires_at},
        get_secret_key(),
        algorithm=JWT_ALGORITHM,
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Validate a bearer token and return its registered user."""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized

    try:
        payload = jwt.decode(
            credentials.credentials,
            get_secret_key(),
            algorithms=[JWT_ALGORITHM],
        )
    except jwt.InvalidTokenError:
        raise unauthorized from None

    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject.isdecimal():
        raise unauthorized

    user = db.get(User, int(subject))
    if user is None:
        raise unauthorized
    return user


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    user_data: UserRegister,
    db: Session = Depends(get_db),
) -> User:
    """Register a user and store only the Argon2 password hash."""
    existing_email = db.scalar(select(User).where(User.email == str(user_data.email)))
    if existing_email is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    existing_username = db.scalar(
        select(User).where(User.username == user_data.username)
    )
    if existing_username is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this username already exists",
        )

    user = User(
        username=user_data.username,
        email=str(user_data.email),
        hashed_password=password_hasher.hash(user_data.password),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this username or email already exists",
        ) from error
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Verify login credentials and return an access token."""
    user = db.scalar(select(User).where(User.email == str(credentials.email)))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        password_is_valid = password_hasher.verify(
            user.hashed_password,
            credentials.password,
        )
    except (VerificationError, InvalidHashError):
        password_is_valid = False

    if not password_is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenResponse(access_token=create_access_token(user.id))
