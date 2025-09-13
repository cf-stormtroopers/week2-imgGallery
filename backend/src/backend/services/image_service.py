import uuid
from datetime import datetime
from backend.models.models import Comment, Image, Album, ImageAlbum, Like
from backend.models.dtos.image import (
    CommentDTO,
    CommentRequestDTO,
    CreateImageDTO,
    ImageResponseDTO,
    AlbumResponseDTO,
)

from sqlmodel import Session, func, select, desc, col
from typing import List, Optional
from PIL import Image as PILImage
import io
from backend.config.minio import add_image_to_minio
from backend.config.qdrant import add_to_qdrant, search_in_qdrant
from backend.config.replicate import generate_embeddings, generate_text_embeddings
from backend.config.settings import settings


class ImageService:
    def __init__(self, session: Session):
        self.session = session

    def get_home_images(self) -> dict:
        images = self.session.exec(select(Image).order_by(desc(Image.timestamp))).all()
        albums = self.session.exec(
            select(Album).order_by(desc(Album.updated_at)).limit(5)
        ).all()
        return {
            "images": [ImageResponseDTO.model_validate(img.__dict__, from_attributes=True) for img in images],
            "albums": [AlbumResponseDTO.model_validate(album.__dict__, from_attributes=True) for album in albums],
        }

    def get_image(
        self, image_id: str, user_id: Optional[uuid.UUID]
    ) -> Optional[ImageResponseDTO]:
        image_id_uuid = uuid.UUID(image_id)
        image = self.session.get(Image, image_id_uuid)
        like_count = self.session.exec(
            select(func.count()).where(Like.image_id == image_id_uuid)
        ).first()
        has_user_liked = False
        if user_id and image:
            like_result = self.session.exec(
                select(func.count()).where(
                    Like.image_id == image_id_uuid, Like.user_id == user_id
                )
            ).first()
            has_user_liked = (like_result or 0) > 0

        if image:
            image.view_count += 1
            self.session.add(image)
            self.session.commit()  # Commit the view count increment
            res = ImageResponseDTO.model_validate(image)
            res.like_count = like_count or 0
            res.user_liked = has_user_liked
            return res
        return None

    def get_image_comments(self, image_id: str) -> List[CommentDTO]:
        image = self.session.get(Image, uuid.UUID(image_id))
        if not image:
            return []
        comments = self.session.exec(
            select(Comment)
            .where(Comment.image_id == image_id)
            .order_by(desc(Comment.timestamp))
        ).all()
        return [CommentDTO.model_validate(comment) for comment in comments]

    def add_comment(
        self, comment_data: CommentRequestDTO, user_id: uuid.UUID
    ) -> Optional[CommentDTO]:
        image = self.session.get(Image, comment_data.image_id)
        if not image:
            return None
        comment = Comment(
            user_id=user_id,
            image_id=uuid.UUID(comment_data.image_id),
            content=comment_data.content or "",
            timestamp=datetime.utcnow(),
        )
        self.session.add(comment)
        self.session.commit()
        self.session.refresh(comment)
        return CommentDTO.model_validate(comment)

    def create_image(
        self, image_data: CreateImageDTO, user_id: uuid.UUID
    ) -> ImageResponseDTO:
        img_file = image_data.file
        if not img_file:
            raise ValueError("No image file provided")

        # Read image bytes and open with PIL
        img_bytes = img_file.file.read()
        pil_img = PILImage.open(io.BytesIO(img_bytes)).convert("RGB")

        # Generate UUID for image
        image_id = str(uuid.uuid4())

        # Create thumbnails
        sizes = {
            "small": (128, 128),
            "medium": (512, 512),
            "large": (1024, 1024),
        }
        thumbnails = {}
        for size_name, size in sizes.items():
            thumb = pil_img.copy()
            thumb.thumbnail(size)
            thumbnails[size_name] = thumb

        # Upload original and thumbnails to Minio
        filenames = {
            "original": f"{image_id}_original.png",
            "small": f"{image_id}_small.png",
            "medium": f"{image_id}_medium.png",
            "large": f"{image_id}_large.png",
        }
        # Upload original
        add_image_to_minio(pil_img, filenames["original"])
        # Upload thumbnails
        for size_name in ["small", "medium", "large"]:
            add_image_to_minio(thumbnails[size_name], filenames[size_name])

        # Dummy embedding (replace with real model later)
        def get_dummy_embedding(image: PILImage.Image) -> list:
            return [0.0] * 128

        embedding = get_dummy_embedding(pil_img)

        # Store image in DB (store only filenames, not Minio URLs)
        image = Image(
            id=uuid.UUID(image_id),
            title=image_data.title,
            caption=image_data.caption,
            alt_text=image_data.alt_text,
            license=image_data.license,
            attribution=image_data.attribution,
            privacy=image_data.privacy,
            created_by=user_id,
            timestamp=(
                datetime.fromisoformat(image_data.timestamp)
                if image_data.timestamp
                else datetime.utcnow()
            ),
            url=filenames["original"],
            mime_type=img_file.content_type or "image/png",
            small_url=filenames["small"],
            medium_url=filenames["medium"],
            large_url=filenames["large"],
            view_count=0,
            download_count=0,
        )
        self.session.add(image)
        self.session.commit()
        self.session.refresh(image)

        # Generate embedding
        embedding = generate_embeddings(pil_img)

        # Add embedding to Qdrant
        add_to_qdrant(
            collection_name="images",
            points=embedding,
            id=image_id,
        )

        # Add many-to-many relationships for albums
        for album_id in image_data.albums:
            image_album = ImageAlbum(
                album_id=uuid.UUID(album_id),
                image_id=uuid.UUID(image_id)
            )
            self.session.add(image_album)
        self.session.commit()

        return ImageResponseDTO.model_validate(image)

    def search_images(self, query: str) -> list:
        # Simple DB search by title/caption/alt_text
        stmt = select(Image).where(
            (col(Image.title).ilike(f"%{query}%"))
            | (col(Image.caption).ilike(f"%{query}%"))
            | (col(Image.alt_text).ilike(f"%{query}%"))
        )
        images = self.session.exec(stmt).all()
        return [ImageResponseDTO.model_validate(img) for img in images]


    def vector_search_images(self, query_vector: list, top_k: int = 10) -> list:
        # Vector search in Qdrant
        results = search_in_qdrant("images", query_vector, top_k)
        if not results:
            return []

        # Extract image IDs with similarity scores, maintaining order
        scored_results = []
        for point in results:
            try:
                image_id = uuid.UUID(str(point.id))
                score = float(point.score) if hasattr(point, 'score') else 0.0
                if score > 0.15:
                    scored_results.append((image_id, score))
            except (ValueError, TypeError):
                continue

        if not scored_results:
            return []

        # Get all images in one query
        image_ids = [result[0] for result in scored_results]
        stmt = select(Image).where(col(Image.id).in_(image_ids))
        images_dict = {img.id: img for img in self.session.exec(stmt).all()}

        # Return images in the order of vector similarity scores
        ordered_images = []
        for image_id, score in scored_results:
            if image_id in images_dict:
                ordered_images.append(ImageResponseDTO.model_validate(images_dict[image_id]))

        return ordered_images

    def combined_search_images(
        self, query: str, top_k: int = 20
    ) -> list:
        """
        Combines text-based and vector-based search results.
        Text matches get priority (faux high similarity), then vector results by actual similarity.
        """
        if not query.strip():
            return []

        # Get exact text matches first (these are most relevant)
        text_results = self.search_images(query)
        
        # Generate embedding for vector search
        print(f"Generating text embeddings for query: '{query}'")
        try:
            query_vector = generate_text_embeddings(query)
            if not query_vector:
                print("Warning: Empty query vector, using text search only")
                return text_results
        except Exception as e:
            print(f"Error generating embeddings: {e}, using text search only")
            return text_results

        print(f"Generated query vector with {len(query_vector)} dimensions")

        # Get vector search results (with similarity cutoff applied)
        vector_results = self.vector_search_images(query_vector, top_k)
        
        # Create final ordered list: exact text matches first, then vector results
        text_ids = {img.id for img in text_results}
        vector_only_results = [img for img in vector_results if img.id not in text_ids]
        
        # Combine: text matches first (highest relevance), then vector similarity
        final_results = text_results + vector_only_results
        
        print(f"Combined search found {len(final_results)} results:")
        print(f"  - {len(text_results)} exact text matches")
        print(f"  - {len(vector_only_results)} vector similarity matches")

        return final_results

    def delete_image(self, image_id: str) -> bool:
        image = self.session.get(Image, uuid.UUID(image_id))
        if not image:
            return False
        self.session.delete(image)
        self.session.commit()
        return True
