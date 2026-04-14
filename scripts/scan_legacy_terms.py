from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {"vendor", "__pycache__", ".git", ".pytest_cache", "tmp"}
TEXT_SUFFIXES = {".py", ".txt", ".json", ".jsx", ".js", ".html", ".css", ".bat", ".ps1"}
LEGACY_TERMS = ("JEPE", "潔沛")


def iter_text_files():
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        if path.name == "scan_legacy_terms.py":
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        yield path


def main() -> int:
    hits: list[tuple[Path, int, str]] = []
    for path in iter_text_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line_no, line in enumerate(text.splitlines(), 1):
            if any(term in line for term in LEGACY_TERMS):
                hits.append((path, line_no, line.strip()))
    if not hits:
        print("OK: no legacy JEPE/潔沛 strings found in tracked text files.")
        return 0
    print("Found legacy terms that should be reviewed:")
    for path, line_no, line in hits:
        print(f"- {path.relative_to(ROOT)}:{line_no}: {line}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
