from __future__ import annotations

import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from src.modules.media.config import (
    CLOUDINARY_API_KEY,
    CLOUDINARY_API_SECRET,
    CLOUDINARY_CLOUD_NAME,
    CLOUDINARY_FOLDER,
    MAX_FILE_SIZE_MB,
    is_cloudinary_configured,
)

router = APIRouter()


def _ensure_cloudinary_config():
    if is_cloudinary_configured():
        cloudinary.config(
            cloud_name=CLOUDINARY_CLOUD_NAME,
            api_key=CLOUDINARY_API_KEY,
            api_secret=CLOUDINARY_API_SECRET,
            secure=True,
        )


@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    if not is_cloudinary_configured():
        return JSONResponse(status_code=503, content={"success": False, "message": "Media storage is not configured"})

    _ensure_cloudinary_config()

    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(status_code=413, detail=f"File exceeds max size of {MAX_FILE_SIZE_MB}MB")

    result = cloudinary.uploader.upload(
        content,
        folder=CLOUDINARY_FOLDER,
        resource_type="auto",
    )

    return JSONResponse(
        status_code=201,
        content={
            "success": True,
            "message": "File uploaded successfully",
            "data": {
                "publicId": result.get("public_id"),
                "secureUrl": result.get("secure_url"),
                "resourceType": result.get("resource_type"),
                "format": result.get("format"),
                "bytes": result.get("bytes"),
            },
        },
    )


@router.delete("/delete")
async def delete(payload: dict):
    if not is_cloudinary_configured():
        return JSONResponse(status_code=503, content={"success": False, "message": "Media storage is not configured"})

    _ensure_cloudinary_config()

    public_id = str(payload.get("publicId") or "").strip()
    resource_type = str(payload.get("resourceType") or "image").strip()
    if not public_id:
        raise HTTPException(status_code=400, detail="publicId is required")

    result = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
    return {"success": True, "message": "File deleted successfully", "data": result}

