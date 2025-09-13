from sqlmodel import Field
import datetime
from typing import Optional
import uuid
from .base import BaseModel

class User(BaseModel, table=True):
    """User model."""

    __tablename__ = "users"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(max_length=50, unique=True, index=True)
    display_name: Optional[str] = Field(default=None, max_length=100)
    password_hash: str = Field(max_length=255)
    role: str = Field(default="public", max_length=50)  # Default role is 'public'


class UserSession(BaseModel, table=True):
    """User session model."""

    __tablename__ = "user_sessions"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    session_token: str = Field(unique=True, index=True)
    expires_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.utcnow() + datetime.timedelta(hours=24))
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

    @classmethod
    def create_session_token(cls) -> str:
        """Generate a secure session token."""
        return str(uuid.uuid4())

    @classmethod
    def get_expiry_time(cls) -> datetime.datetime:
        """Get session expiry time."""
        return datetime.datetime.utcnow() + datetime.timedelta(hours=24)  # Default 24 hours

class Image(BaseModel, table=True):
    """Image model."""

    __tablename__ = "images"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    
    url: str = Field(max_length=255)
    mime_type: str = Field(max_length=50)

    small_url: Optional[str] = Field(default=None, max_length=255)
    medium_url: Optional[str] = Field(default=None, max_length=255)
    large_url: Optional[str] = Field(default=None, max_length=255)

    title: Optional[str] = Field(default=None, max_length=100)
    caption: Optional[str] = Field(default=None)
    alt_text: Optional[str] = Field(default=None, max_length=255)
    license: Optional[str] = Field(default=None, max_length=100)
    attribution: Optional[str] = Field(default=None, max_length=255)

    privacy: str = Field(default="public", max_length=50)  # Default privacy is 'public'
    created_by: uuid.UUID = Field(foreign_key="users.id", index=True)
    timestamp: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.UTC))

    view_count: int = Field(default=0)
    download_count: int = Field(default=0)

class Collection(BaseModel, table=True):
    """Collection model."""

    __tablename__ = "collections"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=100, unique=True)

class Album(BaseModel, table=True):
    """Album model."""

    __tablename__ = "albums"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=100)
    description: Optional[str] = Field(default=None)
    collection_id: uuid.UUID = Field(foreign_key="collections.id", index=True)

class Setting(BaseModel, table=True):
    """Setting model."""

    __tablename__ = "settings"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    key: str = Field(max_length=100, unique=True, index=True)
    value: str = Field(max_length=255)

class ImageAlbum(BaseModel, table=True):
    """Association table for albums and photos."""

    __tablename__ = "image_albums"

    album_id: uuid.UUID = Field(foreign_key="albums.id", primary_key=True)
    image_id: uuid.UUID = Field(foreign_key="images.id", primary_key=True)

class Like(BaseModel, table=True):
    """Like model."""

    __tablename__ = "likes"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    image_id: uuid.UUID = Field(foreign_key="images.id", index=True)

class Comment(BaseModel, table=True):
    """Comment model."""

    __tablename__ = "comments"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    image_id: uuid.UUID = Field(foreign_key="images.id", index=True)
    content: str = Field(max_length=500)
    timestamp: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.UTC))
