
import uuid
from pydantic import field_validator
from backend.models.base import BaseModel
from backend.models.models import Image
from fastapi import UploadFile
from typing import Optional

class ImageResponseDTO(Image):
    user_liked: Optional[bool] = False
    like_count: Optional[int] = 0
    similarity_score: Optional[float] = None
    pass

class CreateImageDTO(BaseModel):
    file: UploadFile
    title: Optional[str] = None
    caption: Optional[str] = None
    alt_text: Optional[str] = None
    license: Optional[str] = None
    attribution: Optional[str] = None
    privacy: str = "public"
    timestamp: Optional[str] = None
    albums: list[str] = []

class AlbumResponseDTO(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    collection_id: str
    collection_name: Optional[str] = None
    
    @field_validator('id', 'collection_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

class AlbumWithImagesResponseDTO(AlbumResponseDTO):
    images: list[ImageResponseDTO] = []

class CommentDTO(BaseModel):
    id: Optional[str] = None
    user_id: str
    image_id: str
    content: str
    timestamp: Optional[str] = None

class CommentRequestDTO(BaseModel):
    image_id: str
    content: str