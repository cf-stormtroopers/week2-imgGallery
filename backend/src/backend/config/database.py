from sqlmodel import SQLModel, create_engine, Session, select
from backend.config import settings
from typing import Generator
from ..models.system import Extension, Setting
from ..models.post import Post, PostData
from ..models.user import User, Role, Permission
from ..utils.auth import hash_password


# Create database engine
engine = create_engine(
    settings.database_url,
    echo=False,  # Log SQL queries in debug mode
    pool_pre_ping=True,   # Verify connections before use
    pool_recycle=300,     # Recycle connections every 5 minutes
)


def create_db_and_tables():
    """Create database tables."""
    print("Creating database tables...")
    print(engine.url)
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Dependency to get database session."""
    with Session(engine) as session:
        yield session

def create_default_settings():
    """Create default system settings if they don't exist."""
    
    with Session(engine) as session:
        settings_data = [
            {"key": "comments_enabled", "value": "true", "description": "Enable comments", "type": "string"},
            {"key": "show_markdown", "value": "true", "description": "Setting for show_markdown", "type": "boolean"},
            {"key": "show_registration", "value": "false", "description": "Setting for show_registration", "type": "boolean"},
            {"key": "show_search", "value": "true", "description": "Setting for show_search", "type": "boolean"},
            {"key": "blog_title", "value": "Stormtrooper Chyrp", "description": "Blog site title", "type": "string"},
        ]
        
        for setting_data in settings_data:
            # Check if setting already exists
            existing = session.exec(
                select(Setting).where(Setting.key == setting_data["key"])
            ).first()
            
            if not existing:
                setting = Setting(**setting_data)
                session.add(setting)
                print(f"Created setting: {setting_data['key']} = {setting_data['value']}")
        
        session.commit()


def create_sample_data():
    """Create sample user and posts for testing."""
    from backend.models.user import User
    from backend.models.post import Post, PostData, PostStatus
    from backend.utils import hash_password
    import uuid
    from datetime import datetime
    
    with Session(engine) as session:
        # Check if sample user already exists
        existing_user = session.exec(
            select(User).where(User.username == "CloneFest2025")
        ).first()
        
        if existing_user:
            print("Sample user already exists")
            return
        
        # Create sample user
        user = User(
            username="CloneFest2025",
            email="clonefest2025@example.com", 
            password_hash=hash_password("CloneFest2025"),
            display_name="Clone Fest 2025",
            bio="Sample user for testing",
            role_id=1  # Will be updated based on actual role
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        print(f"Created sample user: {user.username}")
        
        # Create sample posts
        posts_data = [
            {
                "title": "Test Post 1",
                "slug": "test-post-1",
                "content": "This is the content of the first test post. It contains some sample text to demonstrate the blog functionality."
            },
            {
                "title": "Test Post 2", 
                "slug": "test-post-2",
                "content": "This is the content of the second test post. It has different content to show variety in the blog posts."
            }
        ]
        
        for i, post_info in enumerate(posts_data, 1):
            # Create the post
            post = Post(
                author_id=user.id,
                feather_type="text",
                slug=post_info["slug"],
                title=post_info["title"],
                status=PostStatus.PUBLISHED,
                published_at=datetime.utcnow()
            )
            session.add(post)
            session.commit()
            session.refresh(post)
            
            # Create the post data
            post_data = PostData(
                post_id=post.id,
                content=post_info["content"]
            )
            session.add(post_data)
            print(f"Created sample post: {post_info['title']}")
        
        session.commit()
