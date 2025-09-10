from sqlmodel import Session, select
from typing import Optional
from datetime import datetime
import uuid

from backend.models import UserSession, User
from backend.utils import NotFoundError


class SessionService:
    """Service for session operations."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create_session(self, user_id: uuid.UUID) -> UserSession:
        """Create a new session for user."""
        # Clean up expired sessions for this user
        self.cleanup_expired_sessions(user_id)
        
        session_token = UserSession.create_session_token()
        expires_at = UserSession.get_expiry_time()
        
        user_session = UserSession(
            user_id=user_id,
            session_token=session_token,
            expires_at=expires_at
        )
        
        self.session.add(user_session)
        self.session.commit()
        self.session.refresh(user_session)
        return user_session
    
    def get_session_by_token(self, token: str) -> Optional[UserSession]:
        """Get session by token."""
        statement = select(UserSession).where(
            UserSession.session_token == token,
            UserSession.expires_at > datetime.utcnow()
        )
        return self.session.exec(statement).first()
    
    def get_user_from_session(self, token: str) -> Optional[User]:
        """Get user from session token."""
        user_session = self.get_session_by_token(token)
        if not user_session:
            return None
        
        statement = select(User).where(User.id == user_session.user_id)
        return self.session.exec(statement).first()
    
    def delete_session(self, token: str) -> bool:
        """Delete session by token."""
        statement = select(UserSession).where(UserSession.session_token == token)
        user_session = self.session.exec(statement).first()
        
        if not user_session:
            return False
        
        self.session.delete(user_session)
        self.session.commit()
        return True
    
    def delete_user_sessions(self, user_id: uuid.UUID) -> bool:
        """Delete all sessions for a user."""
        statement = select(UserSession).where(UserSession.user_id == user_id)
        sessions = self.session.exec(statement).all()
        
        for session in sessions:
            self.session.delete(session)
        
        self.session.commit()
        return True
    
    def cleanup_expired_sessions(self, user_id: Optional[uuid.UUID] = None):
        """Clean up expired sessions."""
        statement = select(UserSession).where(UserSession.expires_at <= datetime.utcnow())
        
        if user_id:
            statement = statement.where(UserSession.user_id == user_id)
        
        expired_sessions = self.session.exec(statement).all()
        
        for expired_session in expired_sessions:
            self.session.delete(expired_session)
        
        self.session.commit()
    
    def refresh_session(self, token: str) -> Optional[UserSession]:
        """Refresh session expiry time."""
        user_session = self.get_session_by_token(token)
        if not user_session:
            return None
        
        user_session.expires_at = UserSession.get_expiry_time()
        self.session.add(user_session)
        self.session.commit()
        self.session.refresh(user_session)
        return user_session
