from typing import Optional
from backend.src.backend.models.dtos.auth import UserResponseDTO


class GetSiteInfoDTO:
    user: Optional[UserResponseDTO] = None
    settings: dict = {}

class UpdateSiteSettingsDTO:
    key: str
    value: str

