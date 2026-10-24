"""Public brand identifiers loaded from core/brand.yaml (see docs/BRAND_CLEARANCE.md)."""

from __future__ import annotations

from functools import lru_cache

from . import yamlio
from .fsutil import SKILL_ROOT

DEFAULTS = {
    "status": "PROVISIONAL",
    "display_name": "Raftly",
    "plugin_name": "raftly",
    "marketplace_name": "raftly",
    "skill_command": "forge",
    "package_name": "raftly",
    "repository_name": "raftly",
    "artifact_brand": "Raftly",
    "short_name": "Raftly",
    "state_dir": ".raftly",
    "legacy_state_dirs": [],
}


@lru_cache(maxsize=1)
def brand() -> dict:
    path = SKILL_ROOT / "core" / "brand.yaml"
    data = yamlio.load_file(path) if path.exists() else {}
    return {**DEFAULTS, **{k: v for k, v in (data or {}).items() if v not in (None, "")}}


def name() -> str:
    return brand()["artifact_brand"]
