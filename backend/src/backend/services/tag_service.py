from sqlmodel import Session, select
from typing import Optional, List

from backend.models.taxonomy import Tag, TagCreate
from backend.utils import ConflictError, NotFoundError


class TagService:
    """Service for tag operations."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create_tag(self, tag_data: TagCreate) -> Tag:
        """Create a new tag."""
        # Check if name already exists
        statement = select(Tag).where(Tag.name == tag_data.name)
        existing_tag = self.session.exec(statement).first()
        if existing_tag:
            raise ConflictError("Tag with this name already exists")
        
        # Check if slug already exists
        statement = select(Tag).where(Tag.slug == tag_data.slug)
        existing_tag = self.session.exec(statement).first()
        if existing_tag:
            raise ConflictError("Tag with this slug already exists")
        
        # Create tag
        tag = Tag(
            name=tag_data.name,
            slug=tag_data.slug
        )
        
        self.session.add(tag)
        self.session.commit()
        self.session.refresh(tag)
        return tag
    
    def get_tag_by_id(self, tag_id: int) -> Optional[Tag]:
        """Get tag by ID."""
        statement = select(Tag).where(Tag.id == tag_id)
        return self.session.exec(statement).first()
    
    def get_tag_by_slug(self, slug: str) -> Optional[Tag]:
        """Get tag by slug."""
        statement = select(Tag).where(Tag.slug == slug)
        return self.session.exec(statement).first()
    
    def get_tag_by_name(self, name: str) -> Optional[Tag]:
        """Get tag by name."""
        statement = select(Tag).where(Tag.name == name)
        return self.session.exec(statement).first()
    
    def list_tags(self, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> List[Tag]:
        """List tags with pagination and optional search."""
        statement = select(Tag)
        
        # Add search filter if provided
        if search:
            statement = statement.where(Tag.name.ilike(f"%{search}%"))
        
        statement = statement.order_by(Tag.name).offset(skip).limit(limit)
        return list(self.session.exec(statement).all())
    
    def delete_tag(self, tag_id: int) -> bool:
        """Delete tag."""
        tag = self.get_tag_by_id(tag_id)
        if not tag:
            raise NotFoundError("Tag not found")
        
        # Note: In a production system, you might want to check if the tag
        # is being used by any posts before allowing deletion, or implement
        # soft deletion instead
        
        self.session.delete(tag)
        self.session.commit()
        return True
