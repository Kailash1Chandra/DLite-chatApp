from __future__ import annotations

import asyncio
import os
from typing import Optional

import httpx

from src.jobs.backup_job import (
    append_jsonl,
    backup_path_for_today,
    fetch_messages,
    looks_placeholder,
    to_backup_doc,
)
from src.queues.state_store import load_state, save_state


def env(name: str, default: Optional[str] = None) -> Optional[str]:
    v = os.getenv(name)
    if v is None:
        return default
    v = v.strip()
    return v if v else default


async def run_backup_loop() -> None:
    supabase_url = env("SUPABASE_URL")
    service_role_key = env("SUPABASE_SERVICE_ROLE_KEY")
    backup_interval_seconds = int(env("BACKUP_INTERVAL_SECONDS", "300") or "300")
    backup_batch_size = int(env("BACKUP_BATCH_SIZE", "500") or "500")
    backup_output_dir = env("BACKUP_OUTPUT_DIR", "/data") or "/data"
    state_file = env("BACKUP_STATE_FILE", os.path.join(backup_output_dir, "state.json")) or os.path.join(backup_output_dir, "state.json")

    if looks_placeholder(supabase_url) or looks_placeholder(service_role_key):
        print("[worker-service] backup disabled (missing/placeholder env)")
        while True:
            await asyncio.sleep(3600)

    state = load_state(state_file)
    last_synced_at: Optional[str] = state.get("lastSyncedAt")

    timeout = httpx.Timeout(connect=5.0, read=30.0, write=30.0, pool=5.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        while True:
            try:
                print(f"[worker-service] backup job start lastSyncedAt={last_synced_at}")
                rows = await fetch_messages(
                    client,
                    supabase_url=supabase_url or "",
                    service_role_key=service_role_key or "",
                    batch_size=backup_batch_size,
                    last_synced_at=last_synced_at,
                )
                if not rows:
                    print("[worker-service] no new messages")
                else:
                    docs = [to_backup_doc(r) for r in rows]
                    out_path = backup_path_for_today(backup_output_dir)
                    append_jsonl(out_path, docs)
                    last_synced_at = rows[-1].get("created_at") or last_synced_at
                    save_state(state_file, {"lastSyncedAt": last_synced_at})
                    print(f"[worker-service] wrote={len(docs)} path={out_path} newLastSyncedAt={last_synced_at}")
            except Exception as e:
                print(f"[worker-service] backup job failed: {e}")

            await asyncio.sleep(backup_interval_seconds)

