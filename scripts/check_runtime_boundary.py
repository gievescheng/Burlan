from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_PRIVATE_FILES = [
    ROOT / ".v2_runtime.json",
    ROOT / ".google_calendar_config.json",
    ROOT / ".google_calendar_tokens.json",
    ROOT / ".flask_secret.key",
]


def main() -> int:
    leaked = [path for path in PUBLIC_PRIVATE_FILES if path.exists()]
    if leaked:
        print("Found private runtime files under the public project root:")
        for path in leaked:
            print(f"- {path}")
        return 1
    print("OK: no private runtime files found under the public project root.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
