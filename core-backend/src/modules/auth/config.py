from __future__ import annotations

from src.utils.env import env, looks_placeholder

PORT = int(env("PORT", "4000") or "4000")

SUPABASE_URL = env("SUPABASE_URL")
SUPABASE_ANON_KEY = env("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = env("SUPABASE_SERVICE_ROLE_KEY")

AUTH_JWT_SECRET = env("AUTH_JWT_SECRET") or env("JWT_SECRET") or "dev-only-secret-change-me"


def is_supabase_configured() -> bool:
    return not looks_placeholder(SUPABASE_URL) and not looks_placeholder(SUPABASE_ANON_KEY or SUPABASE_SERVICE_ROLE_KEY)

