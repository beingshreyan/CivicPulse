import os
import uuid
from fastapi import HTTPException, UploadFile
import cloudinary
import cloudinary.uploader

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB

USE_CLOUDINARY = bool(os.getenv("CLOUDINARY_CLOUD_NAME"))
if USE_CLOUDINARY:
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        secure=True,
    )


async def save_uploaded_image(file: UploadFile) -> str:
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only JPG, PNG, and WEBP images are allowed.")

    contents = await file.read()
    if len(contents) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="Image exceeds 5 MB limit.")

    if USE_CLOUDINARY:
        result = cloudinary.uploader.upload(contents, folder="civicpulse")
        return result["secure_url"]

    os.makedirs("uploads", exist_ok=True)
    ext = os.path.splitext(file.filename or "photo.jpg")[1] or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join("uploads", filename)
    with open(filepath, "wb") as f:
        f.write(contents)
    return f"/uploads/{filename}"