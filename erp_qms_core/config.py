from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


SERVICE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = SERVICE_ROOT.parent
DATA_DIR = SERVICE_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

_RUNTIME_CONFIG_PATH = PROJECT_ROOT / "v2_runtime_config.json"


def _load_runtime_config() -> dict:
    if not _RUNTIME_CONFIG_PATH.exists():
        return {}
    try:
        return json.loads(_RUNTIME_CONFIG_PATH.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}


_RC = _load_runtime_config()
_SQLITE_FALLBACK = f"sqlite:///{(DATA_DIR / 'erp_dev.db').as_posix()}"


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv("DATABASE_URL") or str(
        _RC.get("database_url") or _SQLITE_FALLBACK
    )
    database_policy: str = (
        os.getenv("V2_DATABASE_POLICY")
        or str(_RC.get("database_policy") or "dev")
    ).strip().lower()
    host: str = os.getenv("ERP_HOST") or "127.0.0.1"
    port: int = int(os.getenv("ERP_PORT") or "8891")


settings = Settings()
