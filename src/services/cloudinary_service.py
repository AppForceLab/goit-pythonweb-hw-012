from uuid import uuid4

import cloudinary
import cloudinary.uploader

from src.conf.config import settings

cloudinary.config(
    cloud_name=settings.cloudinary_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
    secure=True,
)


async def upload_avatar(file, public_id_prefix="avatars"):
    """Upload image to Cloudinary and return the secure URL."""
    file_content = await file.read()
    public_id = f"{public_id_prefix}/{uuid4()}"
    result = cloudinary.uploader.upload(
        file_content, public_id=public_id, overwrite=True
    )
    return result.get("secure_url")
