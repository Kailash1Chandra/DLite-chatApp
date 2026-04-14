from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx


def looks_placeholder(v: Optional[str]) -> bool:
    if not v:
        return True
    s = v.strip()
    if not s:
        return True
    if "your-project" in s or "your-supabase" in s or "xxxx.supabase.co" in s or "..." in s:
        return True
    return False


def sb_headers(service_role_key: str, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    headers = {"apikey": service_role_key, "authorization": f"Bearer {service_role_key}"}
    if extra:
        headers.update(extra)
    return headers


async def fetch_messages(client: httpx.AsyncClient, *, supabase_url: str, service_role_key: str, batch_size: int, last_synced_at: Optional[str]) -> List[Dict[str, Any]]:
    url = f"{supabase_url.rstrip('/')}/rest/v1/messages"
    params: Dict[str, str] = {
        "select": "id,chat_id,sender_id,content,type,created_at",
        "order": "created_at.asc",
        "limit": str(batch_size),
    }
    if last_synced_at:
        params["created_at"] = f"gt.{last_synced_at}"
    r = await client.get(url, headers=sb_headers(service_role_key), params=params)
    r.raise_for_status()
    return r.json()


def to_backup_doc(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "messageId": row.get("id"),
        "chatId": row.get("chat_id"),
        "senderId": row.get("sender_id"),
        "content": row.get("content"),
        "type": row.get("type"),
        "createdAt": row.get("created_at"),
        "backedUpAt": datetime.now(timezone.utc).isoformat(),
    }


def backup_path_for_today(output_dir: str) -> str:
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return os.path.join(output_dir, f"messages-backup-{day}.jsonl")


def append_jsonl(path: str, docs: List[Dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        for d in docs:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

