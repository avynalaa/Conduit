from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.core.config import settings
from app.core.security import create_access_token, verify_password, get_password_hash
from app.crud import user as crud_user
from app.schemas.user import UserCreate, UserResponse, Token, LoginRequest
from app.models.models import User

router = APIRouter()


def _authenticate_user(db: Session, email: str, password: str) -> User:
    user = crud_user.get_by_email(db, email=email)
    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return user


def _create_token_response(user_id: int) -> dict:
    access_token = create_access_token(
        data={"sub": str(user_id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    responses={400: {"description": "Email or username already taken"}},
)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """Register a new user."""
    user = crud_user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    if user_in.username:
        existing_username = crud_user.get_by_username(db, username=user_in.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

    user_data = user_in.model_dump()
    user_data["hashed_password"] = get_password_hash(user_data.pop("password"))

    db_user = User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.post(
    "/login",
    response_model=Token,
    summary="Login with OAuth2 form",
    responses={401: {"description": "Incorrect email or password"}},
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """OAuth2 compatible token login."""
    user = _authenticate_user(db, email=form_data.username, password=form_data.password)
    return _create_token_response(user.id)


@router.post(
    "/login/json",
    response_model=Token,
    summary="Login with JSON body",
    responses={401: {"description": "Incorrect email or password"}},
)
def login_json(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
) -> Any:
    """JSON-based login endpoint."""
    user = _authenticate_user(db, email=login_data.email, password=login_data.password)
    return _create_token_response(user.id)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
)
def read_users_me(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get current user."""
    return current_user


@router.post(
    "/oauth/google",
    response_model=Token,
    summary="Google OAuth callback",
    responses={501: {"description": "Not yet implemented"}},
)
def oauth_google(
    code: str,
    db: Session = Depends(get_db)
) -> Any:
    """Google OAuth callback - placeholder for implementation."""
    # TODO: Implement Google OAuth flow
    # 1. Exchange code for access token
    # 2. Get user info from Google
    # 3. Create or get user from database
    # 4. Return JWT token
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Google OAuth not yet implemented"
    )


@router.post(
    "/oauth/github",
    response_model=Token,
    summary="GitHub OAuth callback",
    responses={501: {"description": "Not yet implemented"}},
)
def oauth_github(
    code: str,
    db: Session = Depends(get_db)
) -> Any:
    """GitHub OAuth callback - placeholder for implementation."""
    # TODO: Implement GitHub OAuth flow
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="GitHub OAuth not yet implemented"
    )
