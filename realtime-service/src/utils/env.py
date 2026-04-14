from __future__ import annotations

import os
from typing import Optional


def env(name: str, default: Optional[str] = None) -> Optional[str]:
    v = os.getenv(name)
    if v is None:
        return default
    v = v.strip()
    return v if v else default


def looks_placeholder(v: Optional[str]) -> bool:
    if not v:
        return True
    s = v.strip()
    if not s:
        return True
    if "your-project" in s or "your-supabase" in s or "xxxx.supabase.co" in s or "..." in s:
        return True
    return False

