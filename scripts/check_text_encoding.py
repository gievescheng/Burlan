from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {"vendor", "__pycache__", ".git", ".pytest_cache", "tmp"}
TEXT_SUFFIXES = {".py", ".md", ".txt", ".json", ".jsx", ".js", ".html", ".css", ".bat", ".ps1"}


def iter_text_files():
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        yield path


def main() -> int:
    failed: list[str] = []
    suspicious: list[str] = []
    for path in iter_text_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            failed.append(f"{path.relative_to(ROOT)}: cannot decode as UTF-8")
            continue
        if "\ufffd" in text:
            suspicious.append(f"{path.relative_to(ROOT)}: contains replacement character")
    if failed or suspicious:
        print("Encoding issues found:")
        for item in failed + suspicious:
            print(f"- {item}")
        return 1
    print("OK: all scanned text files decode as UTF-8 and contain no replacement characters.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
