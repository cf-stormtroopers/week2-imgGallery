from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
import uuid


class BaseModel(SQLModel):
    """Base model for common functionality."""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

