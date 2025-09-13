from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from backend.config.database import get_session
from backend.models.dtos.image import AlbumResponseDTO, AlbumWithImagesResponseDTO
from typing import Optional
from backend.services.album_service import AlbumService

router = APIRouter(prefix="/albums", tags=["albums"])

@router.get("/", response_model=list[AlbumResponseDTO])
def list_albums(session: Session = Depends(get_session)):
    service = AlbumService(session)
    return service.list_albums()

@router.get("/{album_id}", response_model=AlbumWithImagesResponseDTO)
def get_album(album_id: str, session: Session = Depends(get_session)):
    service = AlbumService(session)
    album = service.get_album(album_id)
    if not album:
        return {"detail": "Album not found"}
    return album

@router.put("/{album_id}", response_model=AlbumResponseDTO)
def update_album(album_id: str, album: AlbumResponseDTO, session: Session = Depends(get_session)):
    service = AlbumService(session)
    updated = service.update_album(album_id, album)
    if not updated:
        raise HTTPException(status_code=404, detail="Album not found")
    return updated

@router.delete("/{album_id}", response_model=dict)
def delete_album(album_id: str, session: Session = Depends(get_session)):
    service = AlbumService(session)
    deleted = service.delete_album(album_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Album not found")
    return {"detail": "Album deleted"}

@router.post("/", response_model=AlbumResponseDTO)
def create_album(album: AlbumResponseDTO, session: Session = Depends(get_session)):
    service = AlbumService(session)
    created = service.create_album(album)
    if not created:
        raise HTTPException(status_code=400, detail="Could not create album")
    return created