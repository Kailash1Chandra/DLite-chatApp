from __future__ import annotations

from typing import Dict, Optional

import httpx
from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse

from src.modules.auth.token import validate_token
from src.modules.chat.config import SUPABASE_URL, is_supabase_configured, sb_key

router = APIRouter()


def _sb_headers(extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    key = sb_key()
    headers = {
        "apikey": key,
        "authorization": f"Bearer {key}",
    }
    if extra:
        headers.update(extra)
    return headers


@router.get("/messages/{chat_id}")
async def get_messages(chat_id: str, authorization: Optional[str] = Header(default=None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        return JSONResponse(status_code=401, content={"success": False, "message": "Missing or invalid authorization header"})

    token = authorization.split(" ", 1)[1].strip()
    user = await validate_token(token, supabase_api_key=sb_key() or None)
    if user is None:
        return JSONResponse(status_code=401, content={"success": False, "message": "Invalid token"})

    if not is_supabase_configured():
        return {"success": True, "chatId": chat_id, "messages": []}

    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/messages"
    params = {
        "select": "id,chat_id,sender_id,content,type,created_at",
        "chat_id": f"eq.{chat_id}",
        "order": "created_at.asc",
        "limit": "200",
    }
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(url, headers=_sb_headers({"authorization": f"Bearer {sb_key()}"}), params=params)
    if r.status_code >= 400:
        return JSONResponse(status_code=503, content={"success": False, "message": "Chat storage is unavailable"})

    return {"success": True, "chatId": chat_id, "messages": r.json()}

