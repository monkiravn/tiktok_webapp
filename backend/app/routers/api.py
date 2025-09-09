"""FastAPI API routes (ported from Flask)."""

from __future__ import annotations

import os
from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..config import settings
from ..db import get_db
from ..models import User
from ..services.tiktok_live_service import tiktok_service
from ..services.video_service import VideoService

router = APIRouter()


@router.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.VERSION,
    }


@router.post("/upload")
async def upload(
    file: Annotated[UploadFile, File(...)],
    db: Annotated[Session, Depends(get_db)],  # reserved for future use
    _user: Annotated[User, Depends(get_current_user)],
):
    try:
        file_bytes = await file.read()
        vs = VideoService(upload_dir=settings.UPLOAD_FOLDER)
        result = vs.process_upload(file.filename, file_bytes)
        return JSONResponse({"success": True, "result": result})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/process-url")
def process_url(
    payload: dict[str, Any], _user: Annotated[User, Depends(get_current_user)]
):
    url = payload.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    # Placeholder logic
    return {"url": url, "status": "processed", "message": "URL processing coming soon"}


@router.get("/download/{filename}")
def download_processed_video(
    filename: str, _user: Annotated[User, Depends(get_current_user)]
):
    vs = VideoService(upload_dir=settings.UPLOAD_FOLDER)
    file_path = vs.get_processed_video_path(filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=filename, media_type="video/mp4")


# TikTok live endpoints


@router.get("/tiktok_live/status")
def api_status():
    return tiktok_service.get_monitoring_status()


@router.post("/tiktok_live/start")
def api_start():
    try:
        success = tiktok_service.start_monitoring()
        return {
            "success": success,
            "message": "Monitoring started"
            if success
            else "Monitoring already running",
        }
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/tiktok_live/stop")
def api_stop():
    try:
        tiktok_service.stop_monitoring()
        return {"success": True, "message": "Monitoring stopped"}
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/tiktok_live/users")
def api_get_users():
    status = tiktok_service.get_monitoring_status()
    return status["users"]


@router.post("/tiktok_live/users")
def api_add_user(payload: dict[str, Any]):
    try:
        username = (payload.get("username") or "").strip()
        if not username:
            raise HTTPException(status_code=400, detail="Username cannot be empty")
        user_id = tiktok_service.add_user(username)
        return {
            "success": True,
            "message": f"User @{username} added to monitoring",
            "user_id": user_id,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:  # noqa: BLE001
        raise HTTPException(
            status_code=500, detail=f"Error adding user: {str(e)}"
        ) from e


@router.delete("/tiktok_live/users/{user_id}")
def api_remove_user(user_id: str):
    try:
        success = tiktok_service.remove_user(user_id)
        if success:
            return {"success": True, "message": "User removed from monitoring"}
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/tiktok_live/get_live_status")
def get_tiktok_live_status(payload: dict[str, Any]):
    try:
        username = payload.get("username")
        if not username:
            raise HTTPException(status_code=400, detail="Username is required")
        room_id = tiktok_service.get_room_id_from_user(username)
        is_live = tiktok_service.live_check(room_id)
        return {"success": True, "is_live": is_live}
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(e)) from e
