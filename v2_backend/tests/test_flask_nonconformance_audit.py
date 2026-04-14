from .test_support import BaseFlaskOperationsTestCase, Document, Path, Workbook, io, load_workbook, mock, ops_data, record_imports, server, zipfile


class FlaskNonconformanceAuditTest(BaseFlaskOperationsTestCase):
    def test_nonconformance_save_delete_and_import(self):
        response = self.client.get("/api/nonconformances")
        self.assertEqual(response.status_code, 200)
        initial_count = len(response.get_json()["items"])

        create_response = self.client.post(
            "/api/nonconformances",
            json={
                "record": {
                    "date": "2026-03-01",
                    "dept": "品管課",
                    "type": "製程異常",
                    "description": "測試用不符合",
                    "severity": "輕微",
                    "responsible": "王小明",
                }
            },
        )
        self.assertEqual(create_response.status_code, 200)
        created_items = create_response.get_json()["items"]
        self.assertEqual(len(created_items), initial_count + 1)
        created_id = created_items[-1]["id"]

        doc = Document()
        doc.add_paragraph("編號： MR15-TEST-001")
        doc.add_paragraph("發現單位：管理部")
        doc.add_paragraph("不符合日期：2026/03/02")
        doc.add_paragraph("不符合事項說明：檢驗時玻璃掉落破裂。 發現者/稽核員：王小明")
        doc.add_paragraph("原因分析：作業中碰撞到 FOSB。")
        doc.add_paragraph("矯正措施：立即清場並重新教育訓練。 預定完成日期：2026/03/03")
        doc.add_paragraph("最終查核確認：■結案日期：2026/03/04")
        doc_path = Path(self.temp_dir.name) / "nc_import.docx"
        doc.save(doc_path)

        import_response = self.client.post(
            "/api/nonconformances/import",
            data={"file": (io.BytesIO(doc_path.read_bytes()), "nc_import.docx")},
            content_type="multipart/form-data",
        )
        self.assertEqual(import_response.status_code, 200)
        draft = import_response.get_json()["draft"]
        self.assertEqual(draft["dept"], "管理部")
        self.assertEqual(draft["responsible"], "王小明")
        self.assertEqual(draft["date"], "2026-03-02")
        self.assertEqual(draft["rootCause"], "作業中碰撞到 FOSB。")
        self.assertEqual(draft["correctiveAction"], "立即清場並重新教育訓練。")
        self.assertEqual(draft["dueDate"], "2026-03-03")
        self.assertEqual(draft["closeDate"], "2026-03-04")
        self.assertEqual(draft["status"], "已關閉")

        delete_response = self.client.delete(f"/api/nonconformances/{created_id}")
        self.assertEqual(delete_response.status_code, 200)
        self.assertEqual(len(delete_response.get_json()["items"]), initial_count)

    def test_nonconformance_import_prefers_filename_id_when_docx_text_is_wrong(self):
        doc = Document()
        doc.add_paragraph("編號： MR20-01(004)A")
        doc.add_paragraph("發現單位：管理部")
        doc.add_paragraph("不符合日期：2026/03/02")
        doc.add_paragraph("不符合事項說明：測試匯入時檔名與內文編號不一致。 發現者/稽核員：王小明")
        doc.add_paragraph("原因分析：內文編號抄寫錯誤。")
        doc.add_paragraph("矯正措施：應優先採用檔名正式編號。 預定完成日期：2026/03/03")
        doc.add_paragraph("最終查核確認：■結案日期：2026/03/04")
        doc_path = Path(self.temp_dir.name) / "20.1不符合及矯正措施報告表MR20-01(003)A.docx"
        doc.save(doc_path)

        import_response = self.client.post(
            "/api/nonconformances/import",
            data={"file": (io.BytesIO(doc_path.read_bytes()), doc_path.name)},
            content_type="multipart/form-data",
        )
        self.assertEqual(import_response.status_code, 200)
        draft = import_response.get_json()["draft"]
        self.assertEqual(draft["id"], "MR20-01(003)A")

    def test_nonconformance_import_supports_fullwidth_date_characters(self):
        doc = Document()
        doc.add_paragraph("編號： MR20-01(009)A")
        doc.add_paragraph("發現單位：管理部")
        doc.add_paragraph("不符合日期：２０２５／１２／０１")
        doc.add_paragraph("不符合事項說明：BL1700短少一桶（２０ＫＧ）。 發現者/稽核員：蔡有為")
        doc.add_paragraph("原因分析：出貨時未注意產品名稱。")
        doc.add_paragraph("矯正措施：加強出貨確認。 預定完成日期：２０２５.１２／０２")
        doc.add_paragraph("最終查核確認：■結案日期：２０２５／１２／０３")
        doc_path = Path(self.temp_dir.name) / "20.1不符合及矯正措施報告表MR20-01(009)A.docx"
        doc.save(doc_path)

        import_response = self.client.post(
            "/api/nonconformances/import",
            data={"file": (io.BytesIO(doc_path.read_bytes()), doc_path.name)},
            content_type="multipart/form-data",
        )
        self.assertEqual(import_response.status_code, 200)
        draft = import_response.get_json()["draft"]
        self.assertEqual(draft["date"], "2025-12-01")
        self.assertEqual(draft["dueDate"], "2025-12-02")
        self.assertEqual(draft["closeDate"], "2025-12-03")

    def test_audit_plan_docx_import_and_attachments(self):
        doc = Document()
        table = doc.add_table(rows=4, cols=6)
        table.rows[0].cells[0].text = "稽核時間: 2026/04/08"
        table.rows[1].cells[0].text = "NO"
        table.rows[1].cells[1].text = "受稽核單位"
        table.rows[1].cells[3].text = "受稽核人員"
        table.rows[1].cells[4].text = "稽核員"
        table.rows[1].cells[5].text = "稽核內容"
        table.rows[2].cells[0].text = "1"
        table.rows[2].cells[1].text = "品管課"
        table.rows[2].cells[3].text = "林佑翰"
        table.rows[2].cells[4].text = "王稽核"
        table.rows[2].cells[5].text = "文件化資訊管制程序"
        doc_path = Path(self.temp_dir.name) / "audit_plan.docx"
        doc.save(doc_path)

        import_response = self.client.post(
            "/api/audit-plans/import",
            data={"file": (io.BytesIO(doc_path.read_bytes()), "audit_plan.docx")},
            content_type="multipart/form-data",
        )
        self.assertEqual(import_response.status_code, 200)
        records = import_response.get_json()["records"]
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["dept"], "品管課")
        self.assertEqual(records[0]["scope"], "文件化資訊管制程序")
        self.assertEqual(records[0]["scheduledDate"], "2026-04-08")

        save_response = self.client.post("/api/audit-plans", json={"records": records})
        self.assertEqual(save_response.status_code, 200)
        saved_id = save_response.get_json()["saved"][0]["id"]

        attachment_response = self.client.get(f"/api/audit-plans/{saved_id}/attachments")
        self.assertEqual(attachment_response.status_code, 200)
        attachments = attachment_response.get_json()["attachments"]
        self.assertEqual(len(attachments), 1)
        self.assertTrue(attachments[0]["text_previewable"])

        preview_response = self.client.get(attachments[0]["preview_text_url"])
        self.assertEqual(preview_response.status_code, 200)
        self.assertIn("audit_plan.docx", preview_response.get_data(as_text=True))

        delete_response = self.client.delete(f"/api/audit-plans/{saved_id}")
        self.assertEqual(delete_response.status_code, 200)

    def test_audit_plans_list_prefers_burlan_annual_source_files(self):
        root = Path(self.temp_dir.name)
        audit_dir = root / "17內部稽核管理程序" / "記錄" / "114年度"
        audit_dir.mkdir(parents=True, exist_ok=True)

        master_path = root / "柏連正式文件主清單.xlsx"
        wb = Workbook()
        ws = wb.active
        ws.append([
            "文件編號", "文件名稱", "負責單位", "主清單版次", "主清單發行日期",
            "實際資料夾位置", "找到的 PDF 檔", "找到的 Word 檔", "暫定正式檔案",
            "判定狀態", "判定原因", "是否納入系統",
        ])
        ws.append(["MP-01", "文件化資訊管制程序", "管理部", "2.0", "2025/07/18", "", "", "", "", "主清單一致", "", "Y"])
        ws.append(["MP-02", "組織全景及風險管理程序", "管理部", "3.0", "2025/07/18", "", "", "", "", "主清單一致", "", "Y"])
        wb.save(master_path)

        doc = Document()
        table = doc.add_table(rows=6, cols=6)
        table.rows[0].cells[0].text = "稽核時間"
        table.rows[0].cells[1].text = "自 2025 年 6 月 23日 09時 00 分 至 2025 年 6 月23日 17 時 00 分"
        table.rows[1].cells[0].text = "稽 核 內 容"
        table.rows[2].cells[0].text = "NO"
        table.rows[2].cells[1].text = "受稽核單位"
        table.rows[2].cells[2].text = "受稽核人員"
        table.rows[2].cells[3].text = "稽核員"
        table.rows[2].cells[4].text = "稽核時間"
        table.rows[2].cells[5].text = "稽核內容"
        table.rows[3].cells[0].text = "1"
        table.rows[3].cells[1].text = "管理部"
        table.rows[3].cells[2].text = "蔡有為"
        table.rows[3].cells[3].text = "程鼎智"
        table.rows[3].cells[4].text = "20分"
        table.rows[3].cells[5].text = "文件化資訊管制程序"
        table.rows[4].cells[0].text = "2"
        table.rows[4].cells[1].text = "管理部"
        table.rows[4].cells[2].text = "蔡有為"
        table.rows[4].cells[3].text = "程鼎智"
        table.rows[4].cells[4].text = "20分"
        table.rows[4].cells[5].text = "組織全景及風險管理程序"
        plan_path = audit_dir / "17.1內部稽核計畫表.docx"
        doc.save(plan_path)

        report_doc = Document()
        report_doc.add_paragraph("114年度品質稽核報告書")
        report_path = audit_dir / "17.5 114年度品質稽核報告書.docx"
        report_doc.save(report_path)

        ops_data.save_records(
            "auditplan",
            [
                {
                    "id": "IA-2025-01",
                    "year": 2025,
                    "period": "下半年",
                    "scheduledDate": "2025-09-04",
                    "dept": "全廠",
                    "scope": "MP-01,MP-02",
                    "auditor": "蔡有為",
                    "auditee": "程鼎智",
                    "status": "已完成",
                    "actualDate": "2025-09-05",
                    "findings": 4,
                    "ncCount": 1,
                    "attachment_paths": [],
                },
                {
                    "id": "IA-2025-02",
                    "year": 2025,
                    "period": "上半年",
                    "scheduledDate": "2025-01-10",
                    "dept": "品管課",
                    "scope": "MP-16",
                    "auditor": "蔡有為",
                    "auditee": "程鼎智",
                    "status": "已完成",
                    "actualDate": "2025-01-10",
                    "findings": 1,
                    "ncCount": 1,
                    "attachment_paths": [],
                },
            ],
        )

        with mock.patch.object(server, "BURLAN_AUDIT_DIR", root / "17內部稽核管理程序" / "記錄"), mock.patch.object(server, "BURLAN_MASTER_LIST_PATH", master_path):
            response = self.client.get("/api/audit-plans")

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["count"], 1)
        self.assertEqual(len(payload["items"]), 1)
        item = payload["items"][0]
        self.assertEqual(item["id"], "IA-2025-01")
        self.assertEqual(item["period"], "年度")
        self.assertEqual(item["scheduledDate"], "2025-06-23")
        self.assertEqual(item["scope"], "MP-01,MP-02")
        self.assertEqual(item["findings"], 4)
        self.assertEqual(item["ncCount"], 1)

    def test_audit_plan_delete_blocks_burlan_source_records(self):
        root = Path(self.temp_dir.name)
        audit_dir = root / "17內部稽核管理程序" / "記錄" / "114年度"
        audit_dir.mkdir(parents=True, exist_ok=True)

        master_path = root / "柏連正式文件主清單.xlsx"
        wb = Workbook()
        ws = wb.active
        ws.append([
            "文件編號", "文件名稱", "負責單位", "主清單版次", "主清單發行日期",
            "實際資料夾位置", "找到的 PDF 檔", "找到的 Word 檔", "暫定正式檔案",
            "判定狀態", "判定原因", "是否納入系統",
        ])
        ws.append(["MP-01", "文件化資訊管制程序", "管理部", "2.0", "2025/07/18", "", "", "", "", "主清單一致", "", "Y"])
        wb.save(master_path)

        doc = Document()
        table = doc.add_table(rows=4, cols=6)
        table.rows[0].cells[0].text = "稽核時間"
        table.rows[0].cells[1].text = "自 2025 年 6 月 23日 09時 00 分 至 2025 年 6 月23日 17 時 00 分"
        table.rows[1].cells[0].text = "稽 核 內 容"
        table.rows[2].cells[0].text = "NO"
        table.rows[2].cells[1].text = "受稽核單位"
        table.rows[2].cells[2].text = "受稽核人員"
        table.rows[2].cells[3].text = "稽核員"
        table.rows[2].cells[4].text = "稽核時間"
        table.rows[2].cells[5].text = "稽核內容"
        table.rows[3].cells[0].text = "1"
        table.rows[3].cells[1].text = "管理部"
        table.rows[3].cells[2].text = "蔡有為"
        table.rows[3].cells[3].text = "程鼎智"
        table.rows[3].cells[4].text = "20分"
        table.rows[3].cells[5].text = "文件化資訊管制程序"
        doc.save(audit_dir / "17.1內部稽核計畫表.docx")

        with mock.patch.object(server, "BURLAN_AUDIT_DIR", root / "17內部稽核管理程序" / "記錄"), mock.patch.object(server, "BURLAN_MASTER_LIST_PATH", master_path):
            response = self.client.delete("/api/audit-plans/IA-2025-01")

        self.assertEqual(response.status_code, 404)
        self.assertIn("不可直接刪除", response.get_json()["error"])

    def test_audit_plan_year_bundle_downloads_zip(self):
        root = Path(self.temp_dir.name)
        audit_dir = root / "17內部稽核管理程序" / "記錄" / "114年度"
        audit_dir.mkdir(parents=True, exist_ok=True)

        master_path = root / "柏連正式文件主清單.xlsx"
        wb = Workbook()
        ws = wb.active
        ws.append([
            "文件編號", "文件名稱", "負責單位", "主清單版次", "主清單發行日期",
            "實際資料夾位置", "找到的 PDF 檔", "找到的 Word 檔", "暫定正式檔案",
            "判定狀態", "判定原因", "是否納入系統",
        ])
        ws.append(["MP-01", "文件化資訊管制程序", "管理部", "2.0", "2025/07/18", "", "", "", "", "主清單一致", "", "Y"])
        wb.save(master_path)

        doc = Document()
        table = doc.add_table(rows=4, cols=6)
        table.rows[0].cells[0].text = "稽核時間"
        table.rows[0].cells[1].text = "自 2025 年 6 月 23日 09時 00 分 至 2025 年 6 月23日 17 時 00 分"
        table.rows[1].cells[0].text = "稽 核 內 容"
        table.rows[2].cells[0].text = "NO"
        table.rows[2].cells[1].text = "受稽核單位"
        table.rows[2].cells[2].text = "受稽核人員"
        table.rows[2].cells[3].text = "稽核員"
        table.rows[2].cells[4].text = "稽核時間"
        table.rows[2].cells[5].text = "稽核內容"
        table.rows[3].cells[0].text = "1"
        table.rows[3].cells[1].text = "管理部"
        table.rows[3].cells[2].text = "蔡有為"
        table.rows[3].cells[3].text = "程鼎智"
        table.rows[3].cells[4].text = "20分"
        table.rows[3].cells[5].text = "文件化資訊管制程序"
        doc.save(audit_dir / "17.1內部稽核計畫表.docx")

        report_doc = Document()
        report_doc.add_paragraph("114年度品質稽核報告書")
        report_doc.save(audit_dir / "17.5 114年度品質稽核報告書.docx")

        with mock.patch.object(server, "BURLAN_AUDIT_DIR", root / "17內部稽核管理程序" / "記錄"), mock.patch.object(server, "BURLAN_MASTER_LIST_PATH", master_path):
            response = self.client.get("/api/audit-plans/year-bundle?year=114年度")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/zip")
        archive = zipfile.ZipFile(io.BytesIO(response.data))
        try:
            names = archive.namelist()
            self.assertTrue(any(name.endswith("README.txt") for name in names))
            self.assertTrue(any(name.endswith("17.1內部稽核計畫表.docx") for name in names))
            self.assertTrue(any(name.endswith("17.5 114年度品質稽核報告書.docx") for name in names))
        finally:
            archive.close()


