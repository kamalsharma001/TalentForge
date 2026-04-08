"""
CloudinaryService — handles all media asset operations.
Supports: resume PDFs, interview recordings, profile avatars.
"""

import logging
from typing import Optional

import cloudinary
import cloudinary.uploader

from app.utils.errors import ServiceUnavailableError

logger = logging.getLogger(__name__)

# Folder conventions inside Cloudinary
FOLDER_RESUMES    = "talentforge/resumes"
FOLDER_RECORDINGS = "talentforge/recordings"
FOLDER_AVATARS    = "talentforge/avatars"


class CloudinaryService:

    # ── Upload ────────────────────────────────────────────────────────────
    @staticmethod
    def upload_resume(file_stream, filename: str, candidate_id: str) -> dict:
        """Upload a resume PDF.  Returns Cloudinary response dict."""
        return CloudinaryService._upload(
            file_stream,
            folder=FOLDER_RESUMES,
            public_id=f"{candidate_id}/{filename}",
            resource_type="raw",          # PDFs are "raw"
            allowed_formats=["pdf", "doc", "docx"],
        )

    @staticmethod
    def upload_recording(file_stream, interview_id: str) -> dict:
        """Upload an interview recording video."""
        return CloudinaryService._upload(
            file_stream,
            folder=FOLDER_RECORDINGS,
            public_id=f"{interview_id}/recording",
            resource_type="video",
        )

    @staticmethod
    def upload_avatar(file_stream, user_id: str) -> dict:
        """Upload a user profile photo."""
        return CloudinaryService._upload(
            file_stream,
            folder=FOLDER_AVATARS,
            public_id=str(user_id),
            resource_type="image",
            transformation=[{"width": 400, "height": 400, "crop": "fill", "gravity": "face"}],
        )

    # ── Delete ────────────────────────────────────────────────────────────
    @staticmethod
    def delete(public_id: str, resource_type: str = "image") -> bool:
        try:
            result = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
            return result.get("result") == "ok"
        except Exception as exc:
            logger.error("Cloudinary delete failed for %s: %s", public_id, exc)
            return False

    # ── Signed URL (for private recordings) ──────────────────────────────
    @staticmethod
    def get_signed_url(public_id: str, resource_type: str = "video", expires_in: int = 3600) -> str:
        import time
        timestamp = int(time.time()) + expires_in
        try:
            return cloudinary.utils.cloudinary_url(
                public_id,
                resource_type=resource_type,
                sign_url=True,
                type="authenticated",
                expires_at=timestamp,
            )[0]
        except Exception as exc:
            logger.error("Failed to generate signed URL: %s", exc)
            raise ServiceUnavailableError("Could not generate media URL.")

    # ── Internal ──────────────────────────────────────────────────────────
    @staticmethod
    def _upload(file_stream, *, folder: str, public_id: str, resource_type: str = "image", **kwargs) -> dict:
        try:
            result = cloudinary.uploader.upload(
                file_stream,
                folder=folder,
                public_id=public_id,
                overwrite=True,
                resource_type=resource_type,
                **kwargs,
            )
            return {
                "cloudinary_id":  result["public_id"],
                "url":            result["secure_url"],
                "file_size_bytes": result.get("bytes"),
                "mime_type":      result.get("format"),
            }
        except Exception as exc:
            logger.error("Cloudinary upload failed: %s", exc)
            raise ServiceUnavailableError(f"Media upload failed: {str(exc)}")
