from __future__ import annotations

import importlib
import json
import os
import shutil
import tempfile
from pathlib import Path

from pypdf import PdfReader

from .config import settings


class OpenDataLoaderUnavailable(RuntimeError):
    pass


def parse_pdf_document(path: Path) -> dict:
    mode = (settings.pdf_parser_mode or "auto").strip().lower()
    if mode == "legacy":
        result = _parse_with_legacy_pypdf(path)
        result["parser_name"] = "legacy_pypdf"
        result["parser_note"] = "已使用舊版 pypdf PDF 解析。"
        return result

    try:
        result = _parse_with_opendataloader(path)
        result["parser_name"] = "opendataloader_pdf"
        result["parser_note"] = "已使用 OpenDataLoader PDF 解析。"
        return result
    except Exception as exc:
        if mode == "opendataloader":
            raise
        result = _parse_with_legacy_pypdf(path)
        result["parser_name"] = "legacy_pypdf"
        result["parser_note"] = f"OpenDataLoader PDF 無法使用，已自動退回舊版 pypdf 解析：{exc}"
        return result


def _parse_with_legacy_pypdf(path: Path) -> dict:
    reader = PdfReader(str(path))
    chunks = []
    pages_text = []
    for idx, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if not text:
            continue
        pages_text.append(text)
        chunks.extend(_chunk_lines(text.splitlines(), page_no=idx))
    return {
        "title": path.stem,
        "file_type": "pdf",
        "full_text": "\n\n".join(pages_text),
        "chunks": chunks,
        "layout_json": "",
        "layout_page_count": 0,
        "layout_element_count": 0,
    }


def _parse_with_opendataloader(path: Path) -> dict:
    java_path = _ensure_java_runtime()
    if java_path is None:
        raise OpenDataLoaderUnavailable("找不到 Java。OpenDataLoader PDF 需要 Java 11 以上環境。")

    try:
        opendataloader_pdf = importlib.import_module("opendataloader_pdf")
    except ModuleNotFoundError as exc:
        raise OpenDataLoaderUnavailable("尚未安裝 opendataloader-pdf 套件。") from exc

    with tempfile.TemporaryDirectory(prefix="odl_pdf_") as output_dir:
        convert_kwargs = {
            "input_path": [str(path)],
            "output_dir": output_dir,
            "format": "markdown,json",
            "use_struct_tree": settings.opendataloader_use_struct_tree,
        }
        if settings.opendataloader_keep_line_breaks:
            convert_kwargs["keep_line_breaks"] = True
        if settings.opendataloader_hybrid_enabled:
            convert_kwargs["hybrid"] = settings.opendataloader_hybrid_backend or "docling-fast"

        opendataloader_pdf.convert(**convert_kwargs)

        markdown_path = _find_output_file(Path(output_dir), path.stem, {".md", ".markdown", ".txt"})
        json_path = _find_output_file(Path(output_dir), path.stem, {".json"})
        markdown_text = markdown_path.read_text(encoding="utf-8") if markdown_path else ""
        json_payload = _load_json_payload(json_path) if json_path else None

    full_text = markdown_text.strip() or _full_text_from_json(json_payload)
    chunks = _chunks_from_json(json_payload) if json_payload else []
    if not chunks:
        chunks = _chunks_from_markdown(markdown_text)
    if not full_text:
        raise OpenDataLoaderUnavailable("OpenDataLoader PDF 沒有輸出可用文字內容。")

    layout_page_count, layout_element_count = _summarize_layout(json_payload)
    return {
        "title": path.stem,
        "file_type": "pdf",
        "full_text": full_text,
        "chunks": chunks,
        "layout_json": json.dumps(json_payload, ensure_ascii=False) if json_payload is not None else "",
        "layout_page_count": layout_page_count,
        "layout_element_count": layout_element_count,
    }


def _ensure_java_runtime() -> str | None:
    java_path = shutil.which("java")
    if java_path:
        return java_path

    java_home = os.environ.get("JAVA_HOME", "").strip()
    candidate_paths = []
    if java_home:
        candidate_paths.append(Path(java_home) / "bin" / "java.exe")
        candidate_paths.append(Path(java_home) / "bin" / "java")

    candidate_paths.extend(
        [
            Path(r"C:\Program Files\Eclipse Adoptium\jdk-17.0.18.8-hotspot\bin\java.exe"),
            Path(r"C:\Program Files\Eclipse Adoptium\jdk-17.0.18.8-hotspot\bin\java"),
        ]
    )

    for candidate in candidate_paths:
        if candidate.exists():
            java_bin = str(candidate.parent)
            os.environ["JAVA_HOME"] = str(candidate.parent.parent)
            os.environ["PATH"] = java_bin + os.pathsep + os.environ.get("PATH", "")
            return str(candidate)
    return None


def _find_output_file(output_dir: Path, stem: str, suffixes: set[str]) -> Path | None:
    matches = [
        item
        for item in output_dir.rglob("*")
        if item.is_file() and item.suffix.lower() in suffixes and (item.stem == stem or item.stem.startswith(stem))
    ]
    if not matches:
        matches = [item for item in output_dir.rglob("*") if item.is_file() and item.suffix.lower() in suffixes]
    if not matches:
        return None
    matches.sort(key=lambda item: (len(item.parts), item.name.lower()))
    return matches[0]


def _load_json_payload(path: Path) -> object | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _full_text_from_json(payload: object | None) -> str:
    texts = []
    for element in _collect_elements(payload):
        text = _element_text(element)
        if text:
            texts.append(text)
    return "\n\n".join(texts).strip()


def _summarize_layout(payload: object | None) -> tuple[int, int]:
    elements = _collect_elements(payload)
    if not elements:
        return 0, 0
    page_numbers = {page_no for page_no in (_extract_page_no(item) for item in elements) if page_no is not None}
    return len(page_numbers), len(elements)


def _chunks_from_json(payload: object | None) -> list[dict]:
    elements = _collect_elements(payload)
    if not elements:
        return []

    chunks: list[dict] = []
    buffer: list[str] = []
    current_len = 0
    current_page: int | None = None
    current_section = ""

    for element in elements:
        text = _element_text(element)
        if not text:
            continue
        page_no = _extract_page_no(element)
        element_type = str(element.get("type") or "").strip().lower()

        if element_type == "heading":
            current_section = text.splitlines()[0][:80]

        if buffer and ((page_no is not None and current_page is not None and page_no != current_page) or current_len + len(text) > 1000):
            chunk_text = "\n".join(buffer).strip()
            if chunk_text:
                chunks.append(
                    {
                        "page_no": current_page,
                        "section_name": current_section or chunk_text.splitlines()[0][:80],
                        "content": chunk_text,
                    }
                )
            buffer = []
            current_len = 0

        if page_no is not None:
            current_page = page_no

        buffer.append(text)
        current_len += len(text)

    if buffer:
        chunk_text = "\n".join(buffer).strip()
        if chunk_text:
            chunks.append(
                {
                    "page_no": current_page,
                    "section_name": current_section or chunk_text.splitlines()[0][:80],
                    "content": chunk_text,
                }
            )
    return chunks


def _chunks_from_markdown(markdown_text: str) -> list[dict]:
    lines = markdown_text.splitlines()
    if not lines:
        return []

    chunks: list[dict] = []
    buffer: list[str] = []
    current_len = 0
    current_section = ""

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#"):
            current_section = line.lstrip("#").strip()[:80]
        if buffer and current_len + len(line) > 900:
            text = "\n".join(buffer).strip()
            if text:
                chunks.append({"page_no": None, "section_name": current_section or text.splitlines()[0][:80], "content": text})
            buffer = []
            current_len = 0
        buffer.append(line)
        current_len += len(line)

    if buffer:
        text = "\n".join(buffer).strip()
        if text:
            chunks.append({"page_no": None, "section_name": current_section or text.splitlines()[0][:80], "content": text})
    return chunks


def _chunk_lines(lines: list[str], *, page_no: int | None = None) -> list[dict]:
    chunks = []
    buffer = []
    current_len = 0
    for line in lines:
        cleaned = line.strip()
        if not cleaned:
            continue
        if current_len + len(cleaned) > 800 and buffer:
            text = "\n".join(buffer)
            chunks.append({"page_no": page_no, "section_name": text.splitlines()[0][:80], "content": text})
            buffer = []
            current_len = 0
        buffer.append(cleaned)
        current_len += len(cleaned)
    if buffer:
        text = "\n".join(buffer)
        chunks.append({"page_no": page_no, "section_name": text.splitlines()[0][:80], "content": text})
    return chunks


def _collect_elements(payload: object | None) -> list[dict]:
    if payload is None:
        return []

    elements: list[dict] = []
    seen: set[int] = set()

    def walk(node: object) -> None:
        node_id = id(node)
        if node_id in seen:
            return
        seen.add(node_id)

        if isinstance(node, list):
            for item in node:
                walk(item)
            return

        if isinstance(node, dict):
            if _looks_like_element(node):
                elements.append(node)
            for value in node.values():
                walk(value)

    walk(payload)
    return elements


def _looks_like_element(node: dict) -> bool:
    if "type" in node and any(key in node for key in ("content", "description", "page number", "page_no")):
        return True
    if "bounding box" in node and any(key in node for key in ("content", "description")):
        return True
    return False


def _extract_page_no(element: dict) -> int | None:
    for key in ("page number", "page_no", "page"):
        value = element.get(key)
        if value in (None, ""):
            continue
        try:
            return int(value)
        except Exception:
            continue
    return None


def _element_text(element: dict) -> str:
    for key in ("content", "description", "caption", "text"):
        value = element.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    value = element.get("content")
    if isinstance(value, list):
        flattened = []
        for item in value:
            if isinstance(item, str) and item.strip():
                flattened.append(item.strip())
            elif isinstance(item, dict):
                text = _element_text(item)
                if text:
                    flattened.append(text)
        return "\n".join(flattened).strip()
    return ""
