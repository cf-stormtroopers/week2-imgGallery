
from typing import Optional
from backend.models.base import BaseModel
from backend.models.dtos.auth import UserResponseDTO

class GetSiteInfoDTO(BaseModel):
    user: Optional[UserResponseDTO] = None
    settings: dict = {}

class UpdateSiteSettingsDTO(BaseModel):
    key: str
    value: str

