from fastapi import Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from datetime import datetime
from typing import Optional

from backend.config.database import get_session
from backend.models import User, UserSession
from backend.utils import AuthenticationError


security = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    session: Session = Depends(get_session),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """Get current authenticated user from session token."""
    
    # Try to get token from Authorization header
    token = None
    if credentials:
        token = credentials.credentials
    
    # If no token in header, try to get from cookies
    if not token:
        token = request.cookies.get("session_token")
    
    if not token:
        return None
    
    # Find session
    statement = select(UserSession).where(
        UserSession.session_token == token,
        UserSession.expires_at > datetime.utcnow()
    )
    user_session = session.exec(statement).first()
    
    if not user_session:
        return None
    
    # Get user
    user_statement = select(User).where(User.id == user_session.user_id)
    user = session.exec(user_statement).first()
    
    return user


async def require_auth(
    current_user: Optional[User] = Depends(get_current_user)
) -> User:
    """Require authentication - raises exception if user not authenticated."""
    if not current_user:
        raise AuthenticationError("Authentication required")
    return current_user


async def get_current_user_optional(
    request: Request,
    session: Session = Depends(get_session),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """Get current authenticated user (optional) - returns None if not authenticated."""
    return await get_current_user(request, session, credentials)
