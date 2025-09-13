from typing import Optional
from backend.models.dtos.site import GetSiteInfoDTO, UpdateSiteSettingsDTO
from sqlmodel import Session, select
from backend.models.models import Setting, User
from backend.models.dtos.auth import UserResponseDTO


class SiteService:
    def __init__(self, session: Session):
        self.session = session

    def get_site_settings(self) -> dict:
        KEYS = ["site_name", "allow_registrations"]
        settings = {}
        for key in KEYS:
            setting = self.session.exec(
                select(Setting).where(Setting.key == key)
            ).first()
            if setting:
                settings[key] = setting.value
        return settings

    def get_site_info(self, user: Optional[User]) -> GetSiteInfoDTO:
        settings = self.get_site_settings()
        print(settings)
        dto = (
            UserResponseDTO(
                id=str(user.id),
                username=user.username,
                display_name=user.display_name,
                role=user.role,
            )
            if user
            else None
        )
        return GetSiteInfoDTO(user=dto, settings=settings)

    def update_site_settings(self, settings: UpdateSiteSettingsDTO) -> dict:
        setting = self.session.exec(
            select(Setting).where(Setting.key == settings.key)
        ).first()
        if setting:
            setting.value = settings.value
            self.session.add(setting)
        else:
            new_setting = Setting(key=settings.key, value=settings.value)
            self.session.add(new_setting)
        self.session.commit()
        return {"detail": "Settings updated"}
