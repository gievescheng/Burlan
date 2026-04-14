from __future__ import annotations

import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from v2_backend.app import pdf_extractors


class PdfExtractorsTest(unittest.TestCase):
    def test_auto_mode_will_fallback_to_legacy_parser(self):
        fake_settings = SimpleNamespace(pdf_parser_mode="auto")
        legacy_result = {
            "title": "sample",
            "file_type": "pdf",
            "full_text": "legacy text",
            "chunks": [],
            "layout_json": "",
            "layout_page_count": 0,
            "layout_element_count": 0,
        }

        with mock.patch.object(pdf_extractors, "settings", fake_settings):
            with mock.patch.object(
                pdf_extractors,
                "_parse_with_opendataloader",
                side_effect=pdf_extractors.OpenDataLoaderUnavailable("找不到 Java"),
            ):
                with mock.patch.object(pdf_extractors, "_parse_with_legacy_pypdf", return_value=legacy_result):
                    result = pdf_extractors.parse_pdf_document(Path("sample.pdf"))

        self.assertEqual(result["parser_name"], "legacy_pypdf")
        self.assertIn("已自動退回", result["parser_note"])
        self.assertEqual(result["full_text"], "legacy text")
        self.assertEqual(result["layout_page_count"], 0)
        self.assertEqual(result["layout_element_count"], 0)

    def test_opendataloader_mode_will_raise_if_environment_not_ready(self):
        fake_settings = SimpleNamespace(pdf_parser_mode="opendataloader")

        with mock.patch.object(pdf_extractors, "settings", fake_settings):
            with mock.patch.object(
                pdf_extractors,
                "_parse_with_opendataloader",
                side_effect=pdf_extractors.OpenDataLoaderUnavailable("尚未安裝 opendataloader-pdf"),
            ):
                with self.assertRaises(pdf_extractors.OpenDataLoaderUnavailable):
                    pdf_extractors.parse_pdf_document(Path("sample.pdf"))

    def test_chunks_from_json_can_keep_page_number_and_heading(self):
        payload = [
            {"type": "heading", "page number": 1, "content": "品質政策"},
            {"type": "paragraph", "page number": 1, "content": "第一頁的內文。"},
            {"type": "paragraph", "page number": 2, "content": "第二頁的內文。"},
        ]

        chunks = pdf_extractors._chunks_from_json(payload)

        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0]["page_no"], 1)
        self.assertEqual(chunks[0]["section_name"], "品質政策")
        self.assertIn("第一頁的內文。", chunks[0]["content"])
        self.assertEqual(chunks[1]["page_no"], 2)

    def test_summarize_layout_counts_pages_and_elements(self):
        payload = [
            {"type": "heading", "page number": 1, "content": "A"},
            {"type": "paragraph", "page number": 1, "content": "B"},
            {"type": "paragraph", "page number": 3, "content": "C"},
        ]

        page_count, element_count = pdf_extractors._summarize_layout(payload)

        self.assertEqual(page_count, 2)
        self.assertEqual(element_count, 3)


if __name__ == "__main__":
    unittest.main()
