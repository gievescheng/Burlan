from __future__ import annotations

import os
import secrets
import shutil
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
PROJECT_KEY = "burlan_qms"
DEFAULT_SHARED_CONFIG_DIR = (Path(os.getenv("APPDATA") or str(PROJECT_ROOT)) / "AutoAudit").resolve()


def _project_key() -> str:
    override = os.getenv("AUTO_AUDIT_PROJECT_KEY", "").strip()
    if override:
        return override
    return PROJECT_KEY


def _default_private_config_dir() -> Path:
    return (DEFAULT_SHARED_CONFIG_DIR / _project_key()).resolve()


def _migrate_shared_runtime_dir(target_dir: Path) -> list[str]:
    if os.getenv("AUTO_AUDIT_CONFIG_DIR"):
        return []
    shared_dir = DEFAULT_SHARED_CONFIG_DIR
    if target_dir == shared_dir or target_dir.exists() or not shared_dir.exists():
        return []
    marker_files = [
        shared_dir / "data" / "operations" / "nonconformance.json",
        shared_dir / "v2_runtime.json",
        shared_dir / "google_calendar_config.json",
        shared_dir / "flask_secret.key",
    ]
    if not any(path.exists() for path in marker_files):
        return []
    target_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(shared_dir, target_dir, dirs_exist_ok=True)
    return [f"shared_runtime_copied -> {target_dir}"]


PRIVATE_CONFIG_DIR = Path(os.getenv("AUTO_AUDIT_CONFIG_DIR") or _default_private_config_dir()).resolve()
_SHARED_RUNTIME_MIGRATIONS = _migrate_shared_runtime_dir(PRIVATE_CONFIG_DIR)
PRIVATE_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
PRIVATE_DATA_DIR = (PRIVATE_CONFIG_DIR / "data").resolve()
PRIVATE_DATA_DIR.mkdir(parents=True, exist_ok=True)

V2_RUNTIME_CONFIG_PATH = PRIVATE_CONFIG_DIR / "v2_runtime.json"
GOOGLE_CONFIG_PATH = PRIVATE_CONFIG_DIR / "google_calendar_config.json"
GOOGLE_TOKEN_PATH = PRIVATE_CONFIG_DIR / "google_calendar_tokens.json"
FLASK_SECRET_PATH = PRIVATE_CONFIG_DIR / "flask_secret.key"

LEGACY_PRIVATE_FILES = {
    PROJECT_ROOT / ".v2_runtime.json": V2_RUNTIME_CONFIG_PATH,
    PROJECT_ROOT / ".google_calendar_config.json": GOOGLE_CONFIG_PATH,
    PROJECT_ROOT / ".google_calendar_tokens.json": GOOGLE_TOKEN_PATH,
    PROJECT_ROOT / ".flask_secret.key": FLASK_SECRET_PATH,
}


def migrate_legacy_private_files() -> list[str]:
    migrated = list(_SHARED_RUNTIME_MIGRATIONS)
    for legacy_path, target_path in LEGACY_PRIVATE_FILES.items():
        if not legacy_path.exists():
            continue
        if target_path.exists():
            try:
                legacy_path.unlink()
            except OSError:
                pass
            continue
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(legacy_path), str(target_path))
        migrated.append(f"{legacy_path.name} -> {target_path}")
    return migrated


def get_or_create_flask_secret() -> str:
    if FLASK_SECRET_PATH.exists():
        value = FLASK_SECRET_PATH.read_text(encoding="utf-8").strip()
        if value:
            return value
    value = secrets.token_urlsafe(48)
    FLASK_SECRET_PATH.write_text(value, encoding="utf-8")
    return value


def public_root_contains_private_files() -> list[Path]:
    return [legacy_path for legacy_path in LEGACY_PRIVATE_FILES if legacy_path.exists()]
