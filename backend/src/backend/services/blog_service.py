import datetime
import logging

logger = logging.getLogger(__name__)

from sqlmodel import Session, select, and_, or_
from typing import List, Optional
import uuid

from ..models.post import Post, PostRead, PostCreate, PostUpdate
from ..models.user import User
from ..models.taxonomy import Category, Tag, PostCategory, PostTag
from ..models.engagement import Like
from ..models.post import PostData
from ..config.database import engine


class BlogService:
    """Service for blog post operations."""

    def __init__(self, session: Session):
        self.session = session

    async def list_posts(
        self,
        skip: int = 0,
        limit: int = 50,
        category: Optional[str] = None,
        tag: Optional[str] = None,
        search: Optional[str] = None,
        status: Optional[str] = None,
        author_id: Optional[uuid.UUID] = None,
        current_user: Optional[User] = None,
    ) -> List[PostRead]:
        """
        List posts with filtering and pagination.

        Includes categories, tags, likes count, and view count.
        Private/draft posts filtered based on user permissions.
        """
        # join with PostData to get content and excerpt
        statement = select(Post, PostData, User).where(
            Post.id == PostData.post_id, Post.author_id == User.id
        )

        # Filter by status (show only published posts for unauthenticated users)
        if not current_user:
            statement = statement.where(Post.status == "published")
        elif status:
            statement = statement.where(Post.status == status)

        # Filter by author
        if author_id:
            statement = statement.where(Post.author_id == author_id)

        # Filter by category
        if category:
            statement = (
                statement.join(PostCategory)
                .join(Category)
                .where(Category.slug == category)
            )

        # Filter by tag
        if tag:
            statement = statement.join(PostTag).join(Tag).where(Tag.slug == tag)

        # Search in title and content
        if search:
            search_filter = or_(
                Post.title.ilike(f"%{search}%"), Post.content.ilike(f"%{search}%")
            )
            statement = statement.where(search_filter)

        # Apply pagination
        statement = statement.offset(skip).limit(limit).order_by(Post.created_at.desc())

        posts = self.session.exec(statement).all()

        # Convert to PostRead with additional data
        post_reads = []
        for post, post_data, author in posts:
            # Get categories
            categories = self._get_post_categories(post.id)

            # Get tags
            tags = self._get_post_tags(post.id)

            # Get likes count
            likes_count = self._get_likes_count(post.id)

            # Create PostRead object
            post_read = PostRead(
                id=post.id,
                author_id=author.id,
                author_name=author.display_name or author.username,
                feather_type=post.feather_type,
                slug=post.slug,
                title=post.title,
                status=post.status,
                published_at=post.published_at,
                is_private=post.is_private,
                view_count=post.view_count,
                created_at=post.created_at,
                updated_at=post.updated_at,
                categories=categories,
                tags=tags,
                likes_count=likes_count,
                content=post_data.content,
                excerpt=post_data.content[:100] if post_data.content else "",
                media_url=post_data.media_url,
                media_type=post_data.media_type,
                quote_source=post_data.quote_source,
                link_url=post_data.link_url,
            )

            post_reads.append(post_read)

        return post_reads

    async def get_post_by_id(
        self, post_id: uuid.UUID, current_user: Optional[User] = None
    ) -> Optional[PostRead]:
        """
        Get a single post by ID with all related data.
        Increments view count for public posts.
        """
        statement = (
            select(Post, PostData, User)
            .where(Post.id == post_id)
            .join(PostData, Post.id == PostData.post_id)
            .join(User, Post.author_id == User.id)
        )

        post_tuple = self.session.exec(statement).first()
        if not post_tuple:
            return None

        post, post_data, author = post_tuple

        # Check if user can view this post
        if post.status != "published" and not current_user:
            return None

        # Increment view count for published posts
        if post.status == "published":
            post.view_count = (post.view_count or 0) + 1
            self.session.add(post)
            self.session.commit()
            self.session.refresh(post)

        # Get additional data
        categories = self._get_post_categories(post.id)
        tags = self._get_post_tags(post.id)
        likes_count = self._get_likes_count(post.id)

        return PostRead(
            id=post.id,
            author_id=author.id,
            author_name=author.display_name or author.username,
            feather_type=post.feather_type,
            slug=post.slug,
            title=post.title,
            status=post.status,
            published_at=post.published_at,
            is_private=post.is_private,
            view_count=post.view_count,
            created_at=post.created_at,
            updated_at=post.updated_at,
            categories=categories,
            tags=tags,
            likes_count=likes_count,
            content=post_data.content,
            excerpt=post_data.content[:100] if post_data.content else "",
            media_url=post_data.media_url,
            media_type=post_data.media_type,
            quote_source=post_data.quote_source,
            link_url=post_data.link_url,
        )

    async def get_post_by_slug(
        self, slug: str, current_user: Optional[User] = None
    ) -> Optional[PostRead]:
        """
        Get a single post by slug with all related data.
        Does not increment view count (that's handled by the controller).
        """
        statement = (
            select(Post, PostData, User)
            .where(Post.slug == slug)
            .join(PostData, Post.id == PostData.post_id)
            .join(User, Post.author_id == User.id)
        )

        post_tuple = self.session.exec(statement).first()
        if not post_tuple:
            return None

        post, post_data, author = post_tuple

        # Check if user can view this post
        if post.status != "published" and not current_user:
            return None

        # Get additional data
        categories = self._get_post_categories(post.id)
        tags = self._get_post_tags(post.id)
        likes_count = self._get_likes_count(post.id)

        return PostRead(
            id=post.id,
            author_id=author.id,
            author_name=author.display_name or author.username,
            feather_type=post.feather_type,
            slug=post.slug,
            title=post.title,
            status=post.status,
            published_at=post.published_at,
            is_private=post.is_private,
            view_count=post.view_count,
            created_at=post.created_at,
            updated_at=post.updated_at,
            categories=categories,
            tags=tags,
            likes_count=likes_count,
            content=post_data.content,
            excerpt=post_data.content[:100] if post_data.content else "",
            media_url=post_data.media_url,
            media_type=post_data.media_type,
            quote_source=post_data.quote_source,
            link_url=post_data.link_url,
        )

    async def create_post(self, post_data: PostCreate, current_user: User) -> PostRead:
        """Create a new post."""
        post = Post(
            feather_type=post_data.feather_type,
            slug=post_data.slug,
            title=post_data.title,
            status=post_data.status,
            is_private=post_data.is_private,
            author_id=current_user.id,
            published_at=(
                None if post_data.status != "published" else datetime.datetime.utcnow()
            ),
        )

        self.session.add(post)
        self.session.commit()
        self.session.refresh(post)

        # add post data
        post_data_entry = PostData(
            post_id=post.id,
            content=post_data.content,
            markdown_content=post_data.markdown_content,
            media_url=post_data.media_url,
            link_url=post_data.link_url,
            media_type=post_data.media_type,
            quote_source=post_data.quote_source,
        )

        self.session.add(post_data_entry)
        self.session.commit()

        # Add categories if provided
        if hasattr(post_data, "categories") and post_data.categories:
            for category_id in post_data.categories:
                post_category = PostCategory(post_id=post.id, category_id=category_id)
                self.session.add(post_category)

        # Add tags if provided
        if hasattr(post_data, "tags") and post_data.tags:
            for tag_id in post_data.tags:
                post_tag = PostTag(post_id=post.id, tag_id=tag_id)
                self.session.add(post_tag)

        self.session.commit()

        return await self.get_post_by_id(post.id, current_user)

    async def update_post(
        self, post_id: uuid.UUID, post_data: PostUpdate, current_user: User
    ) -> Optional[PostRead]:
        """Update an existing post."""
        post = self.session.get(Post, post_id)
        if not post:
            return None

        # TODO: Add authorization check (author or admin)

        # Update base post fields
        update_data = post_data.model_dump(
            exclude_unset=True, exclude={"categories", "tags", "content", "markdown_content", 
                                        "media_url", "link_url", "media_type", "quote_source"}
        )
        for field, value in update_data.items():
            setattr(post, field, value)

        # Handle published_at
        if "status" in update_data:
            if update_data["status"] == "published" and not post.published_at:
                post.published_at = datetime.datetime.utcnow()
            elif update_data["status"] != "published":
                post.published_at = None

        self.session.add(post)
        self.session.commit()

        # Update or create PostData
        post_data_entry = (
            self.session.query(PostData).filter(PostData.post_id == post.id).first()
        )
        if post_data_entry:
            for field in ["content", "markdown_content", "media_url", "link_url", "media_type", "quote_source"]:
                if hasattr(post_data, field) and getattr(post_data, field) is not None:
                    setattr(post_data_entry, field, getattr(post_data, field))
        else:
            post_data_entry = PostData(
                post_id=post.id,
                content=post_data.content,
                markdown_content=post_data.markdown_content,
                media_url=post_data.media_url,
                link_url=post_data.link_url,
                media_type=post_data.media_type,
                quote_source=post_data.quote_source,
            )
            self.session.add(post_data_entry)

        self.session.commit()

        # Update categories
        if hasattr(post_data, "categories") and post_data.categories is not None:
            self.session.query(PostCategory).filter(PostCategory.post_id == post.id).delete()
            for category_id in post_data.categories:
                post_category = PostCategory(post_id=post.id, category_id=category_id)
                self.session.add(post_category)

        # Update tags
        if hasattr(post_data, "tags") and post_data.tags is not None:
            self.session.query(PostTag).filter(PostTag.post_id == post.id).delete()
            for tag_id in post_data.tags:
                post_tag = PostTag(post_id=post.id, tag_id=tag_id)
                self.session.add(post_tag)

        self.session.commit()

        return await self.get_post_by_id(post.id, current_user)


    async def delete_post(self, post_id: uuid.UUID, current_user: User) -> bool:
        """Delete a post."""
        post = self.session.get(Post, post_id)
        if not post:
            return False

        # TODO: Add authorization check (author or admin)

        self.session.delete(post)
        self.session.commit()
        return True

    async def like_post(self, post_id: uuid.UUID, current_user: User) -> bool:
        """Like a post."""
        post = self.session.get(Post, post_id)
        if not post:
            return False

        # Check if already liked
        existing_like = self.session.exec(
            select(Like).where(
                and_(Like.post_id == post_id, Like.user_id == current_user.id)
            )
        ).first()

        if existing_like:
            return False

        # Create like
        like = Like(post_id=post_id, user_id=current_user.id)
        self.session.add(like)
        self.session.commit()
        return True

    async def unlike_post(self, post_id: uuid.UUID, current_user: User) -> bool:
        """Remove like from a post."""
        like = self.session.exec(
            select(Like).where(
                and_(Like.post_id == post_id, Like.user_id == current_user.id)
            )
        ).first()

        if not like:
            return False

        self.session.delete(like)
        self.session.commit()
        return True

    def _get_post_categories(self, post_id: uuid.UUID) -> List[dict]:
        """Get categories for a post."""
        statement = (
            select(Category).join(PostCategory).where(PostCategory.post_id == post_id)
        )
        categories = self.session.exec(statement).all()
        return [
            {"id": cat.id, "name": cat.name, "slug": cat.slug} for cat in categories
        ]

    def _get_post_tags(self, post_id: uuid.UUID) -> List[dict]:
        """Get tags for a post."""
        statement = select(Tag).join(PostTag).where(PostTag.post_id == post_id)
        tags = self.session.exec(statement).all()
        return [{"id": tag.id, "name": tag.name, "slug": tag.slug} for tag in tags]

    def _get_likes_count(self, post_id: uuid.UUID) -> int:
        """Get likes count for a post."""
        statement = select(Like).where(Like.post_id == post_id)
        likes = self.session.exec(statement).all()
        return len(likes)

    async def increment_view_count(self, post_id: uuid.UUID) -> bool:
        """Increment view count for a post."""
        post = self.session.get(Post, post_id)
        if not post:
            return False
        
        post.view_count = (post.view_count or 0) + 1
        self.session.add(post)
        self.session.commit()
        return True
