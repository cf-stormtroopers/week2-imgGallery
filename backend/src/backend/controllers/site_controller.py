
from backend.models.dtos.site import GetSiteInfoDTO, UpdateSiteSettingsDTO
from fastapi import APIRouter, Depends
from sqlmodel import Session
from backend.config.database import get_session
from backend.services.site_service import SiteService
from backend.middleware.auth import get_current_user_optional

router = APIRouter(prefix="/site", tags=["site"])

@router.get("/info", response_model=GetSiteInfoDTO)
def get_site_info(session: Session = Depends(get_session), current_user = Depends(get_current_user_optional)):
    service = SiteService(session)
    return service.get_site_info(current_user)

@router.post("/settings", response_model=dict)
def update_site_settings(settings: UpdateSiteSettingsDTO, session: Session = Depends(get_session)):
    service = SiteService(session)
    return service.update_site_settings(settings)