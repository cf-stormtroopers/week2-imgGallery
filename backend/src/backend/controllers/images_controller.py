import uuid
import json
from backend.models.dtos.image import AlbumResponseDTO, ImageResponseDTO, CreateImageDTO
from fastapi import APIRouter, Depends, Response, HTTPException, File, Form, UploadFile
from typing import Optional
from sqlmodel import Session, select
from backend.config.database import get_session

from backend.services.image_service import ImageService
from backend.config.minio import get_file_bytes_from_minio
from backend.config.settings import settings
from pydantic import BaseModel
from typing import List

from backend.services.album_service import AlbumService
from backend.models.models import Comment, Like, User

router = APIRouter(prefix="/images", tags=["images"])


@router.get("/download/{image_filename}")
def download_image(image_filename: str):
    try:
        file_bytes = get_file_bytes_from_minio(image_filename)
        # Always serve as image/png for now
        return Response(content=file_bytes, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=404, detail="Image not found")


class HomeResponseDTO(BaseModel):
    images: List[ImageResponseDTO]
    albums: List[AlbumResponseDTO]


class CommentResponseDTO(BaseModel):
    id: str
    user_id: str
    image_id: str
    content: str
    timestamp: str
    username: Optional[str] = None


class CommentCreateDTO(BaseModel):
    content: str


class LikeToggleResponseDTO(BaseModel):
    liked: bool
    like_count: int


@router.get("/home", response_model=HomeResponseDTO)
def get_home_images(session: Session = Depends(get_session)):
    service = ImageService(session)
    data = service.get_home_images()
    albums = AlbumService(session).list_albums()
    return HomeResponseDTO(images=data["images"], albums=albums)


@router.get("/{image_id}", response_model=ImageResponseDTO)
def get_image(
    image_id: str,
    session: Session = Depends(get_session),
    user_id: Optional[str] = None,
):
    service = ImageService(session)
    if user_id is not None:
        import uuid

        user_id_val = uuid.UUID(user_id)
    else:
        user_id_val = None
    image = service.get_image(image_id, user_id_val)
    if not image:
        return {"detail": "Image not found"}
    return image


@router.post("/", response_model=ImageResponseDTO)
def create_image(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    caption: Optional[str] = Form(None),
    alt_text: Optional[str] = Form(None),
    license: Optional[str] = Form(None),
    attribution: Optional[str] = Form(None),
    privacy: str = Form("public"),
    timestamp: Optional[str] = Form(None),
    albums: str = Form("[]"),  # JSON string of album IDs
    session: Session = Depends(get_session),
    user_id: Optional[str] = None,
):
    service = ImageService(session)
    # If user_id is not provided, generate a random one for now (should be replaced with auth)
    if user_id is None:
        user_id_val = uuid.uuid4()
    else:
        user_id_val = uuid.UUID(user_id)
    return service.create_image(
        CreateImageDTO(
            file=file,
            title=title,
            caption=caption,
            alt_text=alt_text,
            license=license,
            attribution=attribution,
            privacy=privacy,
            timestamp=timestamp,
            albums=json.loads(albums),
        ),
        user_id_val,
    )


@router.delete("/{image_id}", response_model=dict)
def delete_image(image_id: str, session: Session = Depends(get_session)):
    service = ImageService(session)
    success = service.delete_image(image_id)
    if not success:
        return {"detail": "Image not found"}
    return {"detail": "Image deleted"}

@router.get("/search/", response_model=List[ImageResponseDTO])
def search_images(
    query: str,
    session: Session = Depends(get_session),
):
    service = ImageService(session)
    images = service.combined_search_images(query)
    return images


@router.get("/{image_id}/comments", response_model=List[CommentResponseDTO])
def get_image_comments(
    image_id: str,
    session: Session = Depends(get_session),
):
    # Get comments for the image
    comments = session.exec(
        select(Comment).where(Comment.image_id == uuid.UUID(image_id))
    ).all()
    
    # Get usernames for the comments
    result = []
    for comment in comments:
        user = session.get(User, comment.user_id)
        username = user.username if user else None
        result.append(CommentResponseDTO(
            id=str(comment.id),
            user_id=str(comment.user_id),
            image_id=str(comment.image_id),
            content=comment.content,
            timestamp=comment.timestamp.isoformat(),
            username=username
        ))
    
    return result


@router.post("/{image_id}/comments", response_model=CommentResponseDTO)
def add_comment(
    image_id: str,
    comment_data: CommentCreateDTO,
    session: Session = Depends(get_session),
    user_id: Optional[str] = None,
):
    # For now, use a default user if not provided (should be replaced with auth)
    if user_id is None:
        user_id_val = uuid.UUID("00000000-0000-0000-0000-000000000001")  # Default user
    else:
        user_id_val = uuid.UUID(user_id)
    
    # Create new comment
    comment = Comment(
        user_id=user_id_val,
        image_id=uuid.UUID(image_id),
        content=comment_data.content,
    )
    session.add(comment)
    session.commit()
    session.refresh(comment)
    
    # Get username
    user = session.get(User, comment.user_id)
    username = user.username if user else None
    
    return CommentResponseDTO(
        id=str(comment.id),
        user_id=str(comment.user_id),
        image_id=str(comment.image_id),
        content=comment.content,
        timestamp=comment.timestamp.isoformat(),
        username=username
    )


@router.delete("/{image_id}/comments/{comment_id}")
def delete_comment(
    image_id: str,
    comment_id: str,
    session: Session = Depends(get_session),
    user_id: Optional[str] = None,
):
    comment = session.get(Comment, uuid.UUID(comment_id))
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Check if comment belongs to the image
    if str(comment.image_id) != image_id:
        raise HTTPException(status_code=400, detail="Comment does not belong to this image")
    
    session.delete(comment)
    session.commit()
    return {"detail": "Comment deleted"}


@router.post("/{image_id}/like", response_model=LikeToggleResponseDTO)
def toggle_like(
    image_id: str,
    session: Session = Depends(get_session),
    user_id: Optional[str] = None,
):
    # For now, use a default user if not provided (should be replaced with auth)
    if user_id is None:
        user_id_val = uuid.UUID("00000000-0000-0000-0000-000000000001")  # Default user
    else:
        user_id_val = uuid.UUID(user_id)
    
    # Check if like already exists
    existing_like = session.exec(
        select(Like).where(
            Like.user_id == user_id_val,
            Like.image_id == uuid.UUID(image_id)
        )
    ).first()
    
    if existing_like:
        # Unlike - remove the like
        session.delete(existing_like)
        session.commit()
        liked = False
    else:
        # Like - add the like
        like = Like(
            user_id=user_id_val,
            image_id=uuid.UUID(image_id),
        )
        session.add(like)
        session.commit()
        liked = True
    
    # Get total like count
    from sqlmodel import func
    like_count = session.exec(
        select(func.count()).where(Like.image_id == uuid.UUID(image_id))
    ).first() or 0
    
    return LikeToggleResponseDTO(liked=liked, like_count=like_count)