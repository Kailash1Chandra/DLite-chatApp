from __future__ import annotations

from typing import Optional

from src.utils.env import env

MAX_FILE_SIZE_MB = int(env("MAX_FILE_SIZE_MB", "50") or "50")

CLOUDINARY_CLOUD_NAME: Optional[str] = env("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY: Optional[str] = env("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET: Optional[str] = env("CLOUDINARY_API_SECRET")
CLOUDINARY_FOLDER = env("CLOUDINARY_FOLDER", "d-lite/media") or "d-lite/media"


def is_cloudinary_configured() -> bool:
    return bool(CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET)

