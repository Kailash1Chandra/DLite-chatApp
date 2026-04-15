from __future__ import annotations

from typing import Optional

from src.utils.env import env, looks_placeholder

SUPABASE_URL: Optional[str] = env("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY: Optional[str] = env("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_ANON_KEY: Optional[str] = env("SUPABASE_ANON_KEY")


def is_supabase_configured() -> bool:
    return not looks_placeholder(SUPABASE_URL) and not looks_placeholder(SUPABASE_ANON_KEY or SUPABASE_SERVICE_ROLE_KEY)


def sb_key() -> str:
    return (SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY or "").strip()


def sb_service_role_key() -> str:
    return (SUPABASE_SERVICE_ROLE_KEY or "").strip()

