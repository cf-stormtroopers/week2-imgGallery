from fastapi import APIRouter, Depends, Response, Request
from sqlmodel import Session
from typing import Optional

from backend.config.database import get_session
from backend.models import LoginRequestDTO, CreateUserDTO, UserResponseDTO
from backend.services import UserService, SessionService
from backend.middleware import get_current_user, require_auth
from backend.utils import AuthenticationError, ValidationError


router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponseDTO)
async def register(user_data: CreateUserDTO, session: Session = Depends(get_session)):
    """Register a new user."""
    user_service = UserService(session)
    user = user_service.create_user(user_data)
    return user


@router.post("/login")
async def login(
    user_credentials: LoginRequestDTO,
    response: Response,
    session: Session = Depends(get_session),
):
    """Login user and create session."""
    user_service = UserService(session)
    session_service = SessionService(session)

    # Authenticate user
    user = user_service.authenticate_user(
        user_credentials.username, user_credentials.password
    )

    if not user:
        raise AuthenticationError("Invalid username or password")

    # Create session
    user_session = session_service.create_session(user.id)

    # Set cookie
    response.set_cookie(
        key="session_token",
        value=user_session.session_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=60 * 60 * 24 * 7,  # 7 days
        expires=60 * 60 * 24 * 7,  # redundant but some browsers require it
        path="/",
    )

    return {
        "message": "Login successful",
        "user": UserResponseDTO.model_validate(user),
        "session_token": user_session.session_token,
    }


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    session: Session = Depends(get_session),
    current_user=Depends(require_auth),
):
    """Logout user and delete session."""
    session_service = SessionService(session)

    # Get token from cookie or header
    token = request.cookies.get("session_token")
    if not token:
        # Try header
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    if token:
        session_service.delete_session(token)

    # Clear cookie
    response.delete_cookie("session_token")

    return {"message": "Logout successful"}

