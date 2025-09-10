from sqlmodel import Session, select
from typing import Optional, List
import uuid

from backend.models.comment import Comment, CommentCreate, CommentUpdate, CommentStatus
from backend.models.post import Post
from backend.utils import ConflictError, NotFoundError, AuthorizationError


class CommentService:
    """Service for comment operations."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create_comment(self, post_id: uuid.UUID, comment_data: CommentCreate, user_id: Optional[uuid.UUID] = None, ip_address: Optional[str] = None) -> Comment:
        """Create a new comment."""
        # Check if post exists
        statement = select(Post).where(Post.id == post_id)
        post = self.session.exec(statement).first()
        if not post:
            raise NotFoundError("Post not found")
        
        # Check if parent comment exists (if provided)
        if comment_data.parent_comment_id:
            statement = select(Comment).where(Comment.id == comment_data.parent_comment_id)
            parent_comment = self.session.exec(statement).first()
            if not parent_comment:
                raise NotFoundError("Parent comment not found")
            if parent_comment.post_id != post_id:
                raise ConflictError("Parent comment does not belong to this post")
        
        # Create comment
        comment = Comment(
            post_id=post_id,
            author_id=user_id,
            content=comment_data.content,
            parent_comment_id=comment_data.parent_comment_id,
            author_name=comment_data.author_name,
            author_email=comment_data.author_email,
            author_url=comment_data.author_url,
            ip_address=ip_address,
            status=CommentStatus.PENDING
        )
        
        self.session.add(comment)
        self.session.commit()
        self.session.refresh(comment)
        return comment
    
    def get_comment_by_id(self, comment_id: uuid.UUID) -> Optional[Comment]:
        """Get comment by ID."""
        statement = select(Comment).where(Comment.id == comment_id)
        return self.session.exec(statement).first()
    
    def list_post_comments(self, post_id: uuid.UUID, skip: int = 0, limit: int = 50) -> List[Comment]:
        """List comments for a post (only approved comments)."""
        statement = select(Comment).where(
            Comment.post_id == post_id,
            Comment.status == CommentStatus.APPROVED
        ).order_by(Comment.created_at).offset(skip).limit(limit)
        return list(self.session.exec(statement).all())
    
    def update_comment(self, comment_id: uuid.UUID, comment_data: CommentUpdate, user_id: uuid.UUID) -> Comment:
        """Update comment (author only)."""
        comment = self.get_comment_by_id(comment_id)
        if not comment:
            raise NotFoundError("Comment not found")
        
        # Check if user is the author
        if comment.author_id != user_id:
            raise AuthorizationError("Can only update your own comments")
        
        update_data = comment_data.model_dump(exclude_unset=True)
        
        # Apply updates
        for field, value in update_data.items():
            if field == "status":
                # Regular users can't change status, only admins
                continue
            setattr(comment, field, value)
        
        self.session.add(comment)
        self.session.commit()
        self.session.refresh(comment)
        return comment
    
    def delete_comment(self, comment_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Delete comment (author only)."""
        comment = self.get_comment_by_id(comment_id)
        if not comment:
            raise NotFoundError("Comment not found")
        
        # Check if user is the author
        if comment.author_id != user_id:
            raise AuthorizationError("Can only delete your own comments")
        
        self.session.delete(comment)
        self.session.commit()
        return True
