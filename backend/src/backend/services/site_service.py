from backend.models.dtos.site import GetSiteInfoDTO, UpdateSiteSettingsDTO
from sqlmodel import Session, select
from backend.models.models import Setting


class SiteService:
    def __init__(self, session: Session):
        self.session = session

    def get_site_settings(self) -> dict:
        KEYS = ["site_name", "allow_registrations"]
        settings = {}
        for key in KEYS:
            setting = self.session.exec(select(Setting).where(Setting.key == key)).first()
            if setting:
                settings[key] = setting.value
        return settings

    def get_site_info(self) -> GetSiteInfoDTO:
        settings = self.get_site_settings()
        print(settings)
        return GetSiteInfoDTO(user=None, settings=settings)

    def update_site_settings(self, settings: UpdateSiteSettingsDTO) -> dict:
        # Dummy implementation
        return {"detail": "Settings updated"}
