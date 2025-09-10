from sqlmodel import Session, select
from typing import Optional, List
import uuid

from backend.models.engagement import Like, LikeCreate
from backend.models.post import Post
from backend.utils import ConflictError, NotFoundError, ValidationError


class LikeService:
    """Service for like operations."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create_like(self, post_id: uuid.UUID, like_data: LikeCreate, user_id: Optional[uuid.UUID] = None, ip_address: Optional[str] = None) -> Like:
        """Create a new like."""
        # Validate post_id matches between URL and body
        if like_data.post_id != post_id:
            raise ValidationError("Post ID in URL must match post ID in request body")
        
        # Check if post exists
        statement = select(Post).where(Post.id == post_id)
        post = self.session.exec(statement).first()
        if not post:
            raise NotFoundError("Post not found")
        
        # Check if user already liked this post
        if user_id:
            existing_like = self.session.exec(
                select(Like).where(Like.post_id == post_id, Like.user_id == user_id)
            ).first()
            if existing_like:
                raise ConflictError("You have already liked this post")
        elif ip_address:
            # Check for anonymous like from same IP
            existing_like = self.session.exec(
                select(Like).where(Like.post_id == post_id, Like.ip_address == ip_address, Like.user_id.is_(None))
            ).first()
            if existing_like:
                raise ConflictError("This IP address has already liked this post")
        
        # Create like
        like = Like(
            post_id=post_id,
            user_id=user_id,
            ip_address=ip_address
        )
        
        self.session.add(like)
        self.session.commit()
        self.session.refresh(like)
        return like
    
    def delete_like(self, post_id: uuid.UUID, user_id: Optional[uuid.UUID] = None, ip_address: Optional[str] = None) -> bool:
        """Delete a like."""
        # Find the like to delete
        if user_id:
            statement = select(Like).where(Like.post_id == post_id, Like.user_id == user_id)
        elif ip_address:
            statement = select(Like).where(Like.post_id == post_id, Like.ip_address == ip_address, Like.user_id.is_(None))
        else:
            raise ValidationError("Must provide either user_id or ip_address")
        
        like = self.session.exec(statement).first()
        if not like:
            raise NotFoundError("Like not found")
        
        self.session.delete(like)
        self.session.commit()
        return True
    
    def get_post_likes(self, post_id: uuid.UUID, skip: int = 0, limit: int = 50) -> List[Like]:
        """Get likes for a post."""
        statement = select(Like).where(Like.post_id == post_id).order_by(Like.created_at.desc()).offset(skip).limit(limit)
        return list(self.session.exec(statement).all())
    
    def user_has_liked(self, post_id: uuid.UUID, user_id: Optional[uuid.UUID] = None, ip_address: Optional[str] = None) -> bool:
        """Check if user/IP has liked a post."""
        if user_id:
            statement = select(Like).where(Like.post_id == post_id, Like.user_id == user_id)
        elif ip_address:
            statement = select(Like).where(Like.post_id == post_id, Like.ip_address == ip_address, Like.user_id.is_(None))
        else:
            return False
        
        like = self.session.exec(statement).first()
        return like is not None
