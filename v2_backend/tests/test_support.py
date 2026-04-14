import io
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

from docx import Document
from openpyxl import Workbook, load_workbook

import ops_data
import record_imports
import server
import burlan_document_sources


class BaseFlaskOperationsTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_root = ops_data._STORAGE_ROOT
        self.original_defaults = {kind: list(meta["defaults"]) for kind, meta in ops_data.KIND_META.items()}
        ops_data.set_storage_root(Path(self.temp_dir.name))
        for kind in ops_data.KIND_META:
            ops_data.KIND_META[kind]["defaults"] = []
            ops_data.save_records(kind, [])
        server.app.config["TESTING"] = True
        self.client = server.app.test_client()
        self._responses = []
        self._client_open = self.client.open

        def _tracked_open(*args, **kwargs):
            response = self._client_open(*args, **kwargs)
            self._responses.append(response)
            return response

        self.client.open = _tracked_open

    def tearDown(self):
        for response in self._responses:
            try:
                response.close()
            except Exception:
                pass
        self.client.open = self._client_open
        for kind, defaults in self.original_defaults.items():
            ops_data.KIND_META[kind]["defaults"] = defaults
        ops_data.set_storage_root(self.original_root)
        self.temp_dir.cleanup()
