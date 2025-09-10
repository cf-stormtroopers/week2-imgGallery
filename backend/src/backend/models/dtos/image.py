from backend.src.backend.models.models import Image
from fastapi import UploadFile
from typing import Optional


class ImageResponseDTO(Image):
    pass

# create image dto
class CreateImageDTO:
    # file is a key that must support fastapi UploadFile
    file: UploadFile
    title: Optional[str] = None
    caption: Optional[str] = None
    alt_text: Optional[str] = None
    timestamp: Optional[str] = None
    albums: list[str] = []

# album response dto
class AlbumResponseDTO:
    id: str
    title: str
    description: Optional[str] = None

    collection_id: str
    collection_name: Optional[str] = None

class AlbumWithImagesResponseDTO(AlbumResponseDTO):
    images: list[ImageResponseDTO] = []




