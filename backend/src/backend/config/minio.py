import io
import os
from PIL.Image import Image
from typing import Optional
from minio import Minio

from .settings import settings

minio_client: Optional[Minio] = None

def create_minio_client() -> Minio:
    global minio_client

    print("MinIO settings:", settings.minio_host, settings.minio_root_user, settings.minio_bucket)

    if minio_client is None:
        minio_client = Minio(
            endpoint=settings.minio_host,
            access_key=settings.minio_root_user,
            secret_key=settings.minio_root_password,
            secure=False
        )
        bucket_name = settings.minio_bucket
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)
    return minio_client

def add_image_to_minio(image: Image, path: str) -> str:
    client = create_minio_client()
    bucket_name = settings.minio_bucket
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    client.put_object(
        bucket_name,
        path,
        img_byte_arr,
        length=img_byte_arr.getbuffer().nbytes,
        content_type='image/png'
    )
    return f"{settings.minio_host}/{bucket_name}/{path}"

# get image from minio
def get_file_bytes_from_minio(path: str) -> bytes:
    client = create_minio_client()
    bucket_name = settings.minio_bucket
    response = client.get_object(bucket_name, path)
    return response.read()