from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from runtime_paths import PRIVATE_CONFIG_DIR, V2_RUNTIME_CONFIG_PATH, migrate_legacy_private_files


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SERVICE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DOCUMENT_ROOT = PROJECT_ROOT.parent
DATA_DIR = SERVICE_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
RUNTIME_CONFIG_PATH = V2_RUNTIME_CONFIG_PATH
migrate_legacy_private_files()


def load_runtime_config() -> dict:
    if not RUNTIME_CONFIG_PATH.exists():
        return {}
    try:
        return json.loads(RUNTIME_CONFIG_PATH.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}


RUNTIME_CONFIG = load_runtime_config()


def _as_bool(value, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if not text:
        return default
    return text in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class Settings:
    project_root: Path = PROJECT_ROOT
    service_root: Path = SERVICE_ROOT
    document_root: Path = Path(
        os.getenv("AUTO_AUDIT_DOCUMENT_ROOT")
        or str(RUNTIME_CONFIG.get("document_root") or DEFAULT_DOCUMENT_ROOT)
    ).resolve()
    private_config_dir: Path = PRIVATE_CONFIG_DIR
    database_url: str = os.getenv("DATABASE_URL") or str(RUNTIME_CONFIG.get("database_url") or f"sqlite:///{(DATA_DIR / 'v2_dev.db').as_posix()}")
    database_policy: str = (os.getenv("V2_DATABASE_POLICY") or str(RUNTIME_CONFIG.get("database_policy") or "dev")).strip().lower()
    openrouter_api_key: str = (os.getenv("OPENROUTER_API_KEY") or str(RUNTIME_CONFIG.get("openrouter_api_key") or "")).strip()
    openrouter_model: str = (os.getenv("OPENROUTER_MODEL") or str(RUNTIME_CONFIG.get("openrouter_model") or "nvidia/nemotron-3-super-120b-a12b:free")).strip()
    openrouter_timeout: int = int(os.getenv("OPENROUTER_TIMEOUT") or str(RUNTIME_CONFIG.get("openrouter_timeout") or "45"))
    pdf_parser_mode: str = (os.getenv("V2_PDF_PARSER_MODE") or str(RUNTIME_CONFIG.get("pdf_parser_mode") or "auto")).strip().lower()
    opendataloader_use_struct_tree: bool = _as_bool(os.getenv("V2_ODL_USE_STRUCT_TREE") or RUNTIME_CONFIG.get("opendataloader_use_struct_tree"), False)
    opendataloader_keep_line_breaks: bool = _as_bool(os.getenv("V2_ODL_KEEP_LINE_BREAKS") or RUNTIME_CONFIG.get("opendataloader_keep_line_breaks"), False)
    opendataloader_hybrid_enabled: bool = _as_bool(os.getenv("V2_ODL_HYBRID_ENABLED") or RUNTIME_CONFIG.get("opendataloader_hybrid_enabled"), False)
    opendataloader_hybrid_backend: str = (os.getenv("V2_ODL_HYBRID_BACKEND") or str(RUNTIME_CONFIG.get("opendataloader_hybrid_backend") or "docling-fast")).strip()
    host: str = os.getenv("V2_HOST") or str(RUNTIME_CONFIG.get("host") or "127.0.0.1")
    port: int = int(os.getenv("V2_PORT") or str(RUNTIME_CONFIG.get("port") or "8890"))
    allowed_origins: tuple[str, ...] = (
        "http://127.0.0.1:8888",
        "http://localhost:8888",
        "http://127.0.0.1:8890",
        "http://localhost:8890",
    )


settings = Settings()
