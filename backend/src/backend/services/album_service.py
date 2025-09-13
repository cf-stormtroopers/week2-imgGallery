import uuid
from backend.models.models import Album, Collection, Image, ImageAlbum
from sqlmodel import Session, select, desc
from typing import List, Optional
from backend.models.dtos.image import (
    AlbumResponseDTO,
    AlbumWithImagesResponseDTO,
    ImageResponseDTO,
)


class AlbumService:
    def __init__(self, session: Session):
        self.session = session

    def list_albums(self) -> List[AlbumResponseDTO]:
        albums = self.session.exec(
            select(Album, Collection).join(Collection).order_by(Album.title)
        ).all()
        return [
            AlbumResponseDTO(
                id=str(album.id),
                title=album.title,
                description=album.description,
                collection_id=str(album.collection_id),
                collection_name=collection.name if collection else None,
            )
            for album, collection in albums
        ]

    def get_album(self, album_id: str) -> Optional[AlbumWithImagesResponseDTO]:
        album = self.session.get(Album, uuid.UUID(album_id))
        if not album:
            return None

        # Get collection info
        collection = self.session.get(Collection, album.collection_id)

        # Get images for this album
        images = self.session.exec(
            select(Image)
            .join(ImageAlbum)
            .where(ImageAlbum.album_id == uuid.UUID(album_id))
            .order_by(desc(Image.timestamp))
        ).all()

        return AlbumWithImagesResponseDTO(
            id=str(album.id),
            title=album.title,
            description=album.description,
            collection_id=str(album.collection_id),
            collection_name=collection.name if collection else None,
            images=[ImageResponseDTO.model_validate(image) for image in images],
        )

    def update_album(self, album_id: str, album_data) -> Optional[AlbumResponseDTO]:
        album = self.session.get(Album, uuid.UUID(album_id))
        if not album:
            return None
        album.title = album_data.title
        album.description = album_data.description
        album.collection_id = uuid.UUID(album_data.collection_id)
        self.session.add(album)
        self.session.commit()
        self.session.refresh(album)
        return AlbumResponseDTO(
            id=str(album.id),
            title=album.title,
            description=album.description,
            collection_id=str(album.collection_id),
            collection_name=None,  # Can be filled if needed
        )

    def delete_album(self, album_id: str) -> bool:
        album = self.session.get(Album, uuid.UUID(album_id))
        if not album:
            return False
        self.session.delete(album)
        self.session.commit()
        return True

    def create_album(self, album_data) -> Optional[AlbumResponseDTO]:
        new_album = Album(
            title=album_data.title,
            description=album_data.description,
            collection_id=uuid.UUID(album_data.collection_id),
        )
        self.session.add(new_album)
        self.session.commit()
        self.session.refresh(new_album)
        return AlbumResponseDTO(
            id=str(new_album.id),
            title=new_album.title,
            description=new_album.description,
            collection_id=str(new_album.collection_id),
            collection_name=None,  # Can be filled if needed
        )
