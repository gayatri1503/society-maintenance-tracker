import os
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)


def upload_complaint_photo(file_bytes: bytes, complaint_context: str) -> str:
    """
    Uploads a photo to Cloudinary under a dedicated folder and returns
    the secure HTTPS URL to store on the Complaint record.
    """
    result = cloudinary.uploader.upload(
        file_bytes,
        folder="society_tracker/complaints",
        public_id=complaint_context,
        overwrite=True,
        resource_type="image",
    )
    return result["secure_url"]