from sqlmodel import Session, select
from typing import Optional, List

from backend.models.taxonomy import Category, CategoryCreate, CategoryUpdate
from backend.utils import ConflictError, NotFoundError


class CategoryService:
    """Service for category operations."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create_category(self, category_data: CategoryCreate) -> Category:
        """Create a new category."""
        # Check if name already exists
        statement = select(Category).where(Category.name == category_data.name)
        existing_category = self.session.exec(statement).first()
        if existing_category:
            raise ConflictError("Category with this name already exists")
        
        # Check if slug already exists
        statement = select(Category).where(Category.slug == category_data.slug)
        existing_category = self.session.exec(statement).first()
        if existing_category:
            raise ConflictError("Category with this slug already exists")
        
        # Create category
        category = Category(
            name=category_data.name,
            slug=category_data.slug,
            description=category_data.description
        )
        
        self.session.add(category)
        self.session.commit()
        self.session.refresh(category)
        return category
    
    def get_category_by_id(self, category_id: int) -> Optional[Category]:
        """Get category by ID."""
        statement = select(Category).where(Category.id == category_id)
        return self.session.exec(statement).first()
    
    def get_category_by_slug(self, slug: str) -> Optional[Category]:
        """Get category by slug."""
        statement = select(Category).where(Category.slug == slug)
        return self.session.exec(statement).first()
    
    def get_category_by_name(self, name: str) -> Optional[Category]:
        """Get category by name."""
        statement = select(Category).where(Category.name == name)
        return self.session.exec(statement).first()
    
    def list_categories(self, skip: int = 0, limit: int = 100) -> List[Category]:
        """List categories with pagination."""
        statement = select(Category).order_by(Category.name).offset(skip).limit(limit)
        return list(self.session.exec(statement).all())
    
    def update_category(self, category_id: int, category_data: CategoryUpdate) -> Category:
        """Update category."""
        category = self.get_category_by_id(category_id)
        if not category:
            raise NotFoundError("Category not found")
        
        update_data = category_data.model_dump(exclude_unset=True)
        
        # Check for conflicts if name or slug is being updated
        if 'name' in update_data:
            existing_category = self.get_category_by_name(update_data['name'])
            if existing_category and existing_category.id != category_id:
                raise ConflictError("Category with this name already exists")
        
        if 'slug' in update_data:
            existing_category = self.get_category_by_slug(update_data['slug'])
            if existing_category and existing_category.id != category_id:
                raise ConflictError("Category with this slug already exists")
        
        # Apply updates
        for field, value in update_data.items():
            setattr(category, field, value)
        
        self.session.add(category)
        self.session.commit()
        self.session.refresh(category)
        return category
    
    def delete_category(self, category_id: int) -> bool:
        """Delete category."""
        category = self.get_category_by_id(category_id)
        if not category:
            raise NotFoundError("Category not found")
        
        # Note: In a production system, you might want to check if the category
        # is being used by any posts before allowing deletion, or implement
        # soft deletion instead
        
        self.session.delete(category)
        self.session.commit()
        return True
