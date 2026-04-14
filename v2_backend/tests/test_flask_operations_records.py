from .test_support import BaseFlaskOperationsTestCase, Document, Path, Workbook, io, load_workbook, mock, ops_data, record_imports, server, zipfile


class FlaskOperationsRecordsTest(BaseFlaskOperationsTestCase):
    def test_environment_import_filter_and_delete_range(self):
        wb = Workbook()
        ws = wb.active
        ws.title = "Clean_Long"
        ws.append(["Model:9303"])
        ws.append(["Count Mode:Σ"])
        ws.append(["Number of Samples: 2"])
        ws.append(["Channel", "", "Min", "Max"])
        ws.append(["1(0.3)"])
        ws.append(["2(0.5)"])
        ws.append(["3(5.0)"])
        ws.append(["Date", "Point", "DateTime", "Record", "Ch1(um)", "Ch1_count", "Ch2(um)", "Ch2_count", "Ch3(um)", "Ch3_count", "SampleTime", "HoldTime"])
        ws.append(["2026/03/01", 1, "2026/03/01 08:00:00", 1, 0.3, 100, 0.5, 20, 5.0, 3, "00:01:00", "00:00:05"])
        ws.append(["2026/03/05", 2, "2026/03/05 08:00:00", 2, 0.3, 1500, 0.5, 900, 5.0, 40, "00:01:00", "00:00:05"])
        ws.append(["2026/03/06 09:10:11", "", "", "0.3", "", 61, "", "0.5", 4, "", "", "5.0"])
        sample_path = Path(self.temp_dir.name) / "environment_clean_long.xlsx"
        wb.save(sample_path)

        import_response = self.client.post(
            "/api/environment-records/import",
            data={"file": (io.BytesIO(sample_path.read_bytes()), "environment_clean_long.xlsx")},
            content_type="multipart/form-data",
        )
        self.assertEqual(import_response.status_code, 200)
        records = import_response.get_json()["records"]
        self.assertEqual(len(records), 3)
        self.assertEqual(records[0]["location"], "粒子計數點 1 (08:00:00)")
        self.assertEqual(records[2]["location"], "粒子計數點 1 (09:10:11)")
        self.assertEqual(records[2]["point"], "1")
        self.assertEqual(records[2]["particles03"], 61)
        self.assertEqual(records[2]["particles05"], 4)

        save_response = self.client.post(
            "/api/environment-records",
            json={"records": records, "replace_source_file": records[0]["source_file"]},
        )
        self.assertEqual(save_response.status_code, 200)
        self.assertEqual(len(save_response.get_json()["items"]), 3)

        second_save_response = self.client.post(
            "/api/environment-records",
            json={"records": records, "replace_source_file": records[0]["source_file"]},
        )
        self.assertEqual(second_save_response.status_code, 200)
        self.assertEqual(len(second_save_response.get_json()["items"]), 3)

        filter_response = self.client.get("/api/environment-records?start=2026-03-02&end=2026-03-31")
        self.assertEqual(filter_response.status_code, 200)
        payload = filter_response.get_json()
        self.assertEqual(len(payload["items"]), 2)
        self.assertEqual(payload["summary"]["failed"], 1)

        delete_response = self.client.post(
            "/api/environment-records/delete-range",
            json={"start": "2026-03-01", "end": "2026-03-03"},
        )
        self.assertEqual(delete_response.status_code, 200)
        deleted_payload = delete_response.get_json()
        self.assertEqual(len(deleted_payload["items"]), 2)
        self.assertEqual(deleted_payload["removed_count"], 1)

    def test_environment_template_style_import(self):
        wb = Workbook()
        ws = wb.active
        ws.title = "環境監控資料"
        ws.append(["Date", "DateTime", "Point", "Location", "0.3um", "0.5um", "5.0um", "Temp", "Humidity", "Pressure", "Operator", "Result"])
        ws.append(["日期格式", "量測時間", "1~14", "可留白", "0.3", "0.5", "5.0", "可留白", "可留白", "可留白", "記錄者", "可留白"])
        ws.append(["2026-03-10", "2026-03-10 08:30:00", "3", "", 120, 15, 2, "", "", "", "王小明", ""])
        ws.append(["2026-03-10", "2026-03-10 09:00:00", "", "A區溫濕度測點", "", "", "", 22.4, 46.0, 11.5, "陳小華", ""])
        guide = wb.create_sheet("填寫說明")
        guide["A1"] = "說明頁"
        sample_path = Path(self.temp_dir.name) / "environment_template.xlsx"
        wb.save(sample_path)

        import_response = self.client.post(
            "/api/environment-records/import",
            data={"file": (io.BytesIO(sample_path.read_bytes()), "environment_template.xlsx")},
            content_type="multipart/form-data",
        )
        self.assertEqual(import_response.status_code, 200)
        records = import_response.get_json()["records"]
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["point"], "3")
        self.assertEqual(records[0]["location"], "粒子計數點 3")
        self.assertEqual(records[0]["particles03"], 120)
        self.assertEqual(records[0]["particles05"], 15)
        self.assertEqual(records[0]["particles5"], 2)
        self.assertEqual(records[1]["temp"], 22.4)

    def test_calibration_update_is_saved_and_merged_into_burlan_instruments(self):
        save_response = self.client.post(
            "/api/calibration-records",
            json={
                "record": {
                    "instrumentId": "BRA-02",
                    "instrumentName": "多功能測量儀器",
                    "calibrationDate": "2026-03-30",
                    "nextCalibration": "2026-09-29",
                    "calibMethod": "內校",
                    "status": "合格",
                    "operator": "測試員",
                    "note": "測試保存校正更新",
                }
            },
        )
        self.assertEqual(save_response.status_code, 200)
        payload = save_response.get_json()
        self.assertEqual(payload["manual_update_count"], 1)
        self.assertEqual(payload["saved"][0]["instrumentId"], "BRA-02")

        target = next(item for item in payload["items"] if item["id"] == "BRA-02")
        self.assertEqual(target["calibratedDate"], "2026-03-30")
        self.assertEqual(target["nextCalibration"], "2026-09-29")
        self.assertEqual(target["manualOperator"], "測試員")
        self.assertEqual(target["manualNote"], "測試保存校正更新")

        list_response = self.client.get("/api/calibration-records")
        self.assertEqual(list_response.status_code, 200)
        saved_items = list_response.get_json()["items"]
        self.assertEqual(len(saved_items), 1)
        self.assertEqual(saved_items[0]["instrumentId"], "BRA-02")

    def test_calibration_manual_update_recalculates_next_date_when_saved_value_is_blank(self):
        ops_data.upsert_records(
            "calibration",
            [
                {
                    "instrumentId": "BRA-77",
                    "instrumentName": "測試量具",
                    "calibrationDate": "2025-11-15",
                    "nextCalibration": "",
                    "calibMethod": "外校",
                    "status": "合格",
                    "frequencyLabel": "每年",
                }
            ],
        )

        root = Path(self.temp_dir.name)
        calibration_dir = root / "9量測資源管理程序"
        records_dir = calibration_dir / "記錄"
        records_dir.mkdir(parents=True)

        inventory_path = records_dir / "9.1量規儀器一覽表.docx"
        inventory_path.write_bytes(b"placeholder")

        inventory_map = {
            "BRA-77": {
                "id": "BRA-77",
                "name": "測試量具",
                "frequencyLabel": "每年",
                "calibMethod": "外校",
                "location": "品管課",
                "keeper": "王小明",
                "inventoryPath": str(inventory_path),
            }
        }

        with mock.patch.object(server, "BURLAN_CALIBRATION_DIR", calibration_dir), \
             mock.patch.object(server, "_load_calibration_inventory", return_value=(inventory_map, inventory_path)):
            payload = server.load_burlan_calibration_instruments()

        item = next(entry for entry in payload["items"] if entry["id"] == "BRA-77")
        self.assertEqual(item["calibratedDate"], "2025-11-15")
        self.assertEqual(item["nextCalibration"], "2026-11-15")

    def test_training_records_save_and_delete(self):
        response = self.client.post(
            "/api/training-records",
            json={
                "record": {
                    "id": "EMP-900",
                    "name": "測試員工",
                    "dept": "管理部",
                    "role": "專員",
                    "hireDate": "2026-03-01",
                    "trainings": [
                        {
                            "id": "EMP-900-T01",
                            "course": "內部稽核員訓練",
                            "date": "2026-03-20",
                            "type": "外訓",
                            "result": "合格",
                            "cert": "有",
                            "validUntil": "2027-03-20",
                        }
                    ],
                }
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        saved = next(item for item in payload["items"] if item["id"] == "EMP-900")
        self.assertEqual(saved["name"], "測試員工")
        self.assertEqual(len(saved["trainings"]), 1)
        self.assertEqual(saved["trainings"][0]["course"], "內部稽核員訓練")
        self.assertEqual(saved["trainings"][0]["validUntil"], "2027-03-20")

        list_response = self.client.get("/api/training-records")
        self.assertEqual(list_response.status_code, 200)
        listed = next(item for item in list_response.get_json()["items"] if item["id"] == "EMP-900")
        self.assertEqual(listed["dept"], "管理部")

        delete_response = self.client.delete("/api/training-records/EMP-900")
        self.assertEqual(delete_response.status_code, 200)
        remaining_ids = {item["id"] for item in delete_response.get_json()["items"]}
        self.assertNotIn("EMP-900", remaining_ids)

    def test_equipment_records_save_history_and_delete(self):
        response = self.client.post(
            "/api/equipment-records",
            json={
                "record": {
                    "id": "EQ-900",
                    "name": "測試設備",
                    "location": "品管課",
                    "owner": "王小明",
                    "intervalDays": 45,
                    "lastMaintenance": "2026-03-10",
                    "nextItems": ["清潔", "點檢"],
                    "maintenanceHistory": [
                        {
                            "id": "EQ-900-M001",
                            "date": "2026-03-10",
                            "operator": "王小明",
                            "remark": "首次保養",
                            "items": ["清潔", "點檢"],
                        }
                    ],
                }
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        saved = next(item for item in payload["items"] if item["id"] == "EQ-900")
        self.assertEqual(saved["nextMaintenance"], "2026-04-24")
        self.assertEqual(saved["maintenanceHistory"][0]["operator"], "王小明")
        self.assertEqual(saved["nextItems"], ["清潔", "點檢"])

        list_response = self.client.get("/api/equipment-records")
        self.assertEqual(list_response.status_code, 200)
        listed = next(item for item in list_response.get_json()["items"] if item["id"] == "EQ-900")
        self.assertEqual(listed["location"], "品管課")

        delete_response = self.client.delete("/api/equipment-records/EQ-900")
        self.assertEqual(delete_response.status_code, 200)
        remaining_ids = {item["id"] for item in delete_response.get_json()["items"]}
        self.assertNotIn("EQ-900", remaining_ids)

    def test_equipment_records_recalculate_next_maintenance_when_interval_changes(self):
        response = self.client.post(
            "/api/equipment-records",
            json={
                "record": {
                    "id": "EQ-901",
                    "name": "週期調整設備",
                    "location": "生產課",
                    "owner": "陳小華",
                    "intervalDays": 365,
                    "lastMaintenance": "2025-05-26",
                }
            },
        )
        self.assertEqual(response.status_code, 200)
        listed = next(item for item in response.get_json()["items"] if item["id"] == "EQ-901")
        self.assertEqual(listed["nextMaintenance"], "2026-05-26")

    def test_supplier_records_save_history_and_delete(self):
        response = self.client.post(
            "/api/supplier-records",
            json={
                "record": {
                    "id": "SUP-900",
                    "name": "測試供應商",
                    "category": "化學品",
                    "contact": "王小明",
                    "evalIntervalDays": 180,
                    "lastEvalDate": "2026-03-15",
                    "evalScore": 88,
                    "evalResult": "合格",
                    "issues": ["交期需改善"],
                    "evalHistory": [
                        {
                            "id": "SUP-900-E001",
                            "date": "2026-03-15",
                            "score": 88,
                            "result": "合格",
                            "operator": "採購員",
                            "remark": "整體表現穩定",
                            "issues": ["交期需改善"],
                        }
                    ],
                }
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        saved = next(item for item in payload["items"] if item["id"] == "SUP-900")
        self.assertEqual(saved["name"], "測試供應商")
        self.assertEqual(saved["evalScore"], 88)
        self.assertEqual(saved["issues"], ["交期需改善"])
        self.assertEqual(saved["evalHistory"][0]["operator"], "採購員")

        list_response = self.client.get("/api/supplier-records")
        self.assertEqual(list_response.status_code, 200)
        listed = next(item for item in list_response.get_json()["items"] if item["id"] == "SUP-900")
        self.assertEqual(listed["contact"], "王小明")

        delete_response = self.client.delete("/api/supplier-records/SUP-900")
        self.assertEqual(delete_response.status_code, 200)
        remaining_ids = {item["id"] for item in delete_response.get_json()["items"]}
        self.assertNotIn("SUP-900", remaining_ids)

    def test_burlan_master_documents_return_pdf_and_word_paths(self):
        root = Path(self.temp_dir.name)
        folder = root / "docs" / "MP-01"
        folder.mkdir(parents=True)
        pdf_path = folder / "文件化資訊管制程序2.0.pdf"
        word_path = folder / "文件化資訊管制程序2.0.docx"
        pdf_path.write_bytes(b"%PDF-1.4 test")
        word_path.write_bytes(b"PK test")

        wb = Workbook()
        ws = wb.active
        ws.append(["文件編號", "文件名稱", "負責單位", "主清單版次", "主清單發行日期", "實際資料夾位置", "暫定正式檔案", "找到的 PDF 檔", "找到的 Word 檔", "判定狀態", "判定原因", "是否納入系統"])
        ws.append(["MP-01", "文件化資訊管制程序", "管理部", "2.0", "2025-01-01", str(folder), word_path.name, pdf_path.name, word_path.name, "主清單一致", "", "是"])
        master_path = root / "柏連正式文件主清單.xlsx"
        wb.save(master_path)

        with mock.patch.object(server, "BURLAN_MASTER_LIST_PATH", master_path):
            payload = server.load_burlan_master_documents()

        self.assertEqual(payload["count"], 1)
        item = payload["items"][0]
        self.assertEqual(item["path"], str(word_path))
        self.assertEqual(item["pdf_path"], str(pdf_path))
        self.assertEqual(item["word_path"], str(word_path))

    def test_file_view_allows_absolute_pdf_under_burlan_root(self):
        root = Path(self.temp_dir.name)
        project_dir = root / "project"
        burlan_root = project_dir.parent
        target_dir = burlan_root / "0 品質手冊"
        target_dir.mkdir(parents=True)
        pdf_path = target_dir / "品質手冊.pdf"
        pdf_path.write_bytes(b"%PDF-1.4 test file")

        with mock.patch.object(ops_data, "BASE_DIR", project_dir), \
             mock.patch.object(server, "BASE_DIR", project_dir):
            response = self.client.get("/api/files/view", query_string={"path": str(pdf_path)})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Content-Type"), "application/pdf")

    def test_burlan_quality_objectives_reads_latest_docx(self):
        objective_dir = Path(self.temp_dir.name) / "3 目標管理程序" / "記錄"
        objective_dir.mkdir(parents=True)
        objective_path = objective_dir / "3.1品質目標管制表(115年度).docx"

        doc = Document()
        table = doc.add_table(rows=5, cols=20)
        rows = [
            ["項次", "品質政策", "品質目標", "部門", "投入資源", "衡量方式", "114年度", "114年度", "114年度", "114年度", "114年度", "114年度", "114年度", "114年度", "114年度", "114年度", "114年度", "114年度", "114年度", "備註"],
            ["項次", "品質政策", "品質目標", "部門", "投入資源", "衡量方式", "月項目", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "備註"],
            ["1", "品質穩定", "出貨時間穩定", "管理部", "資材課員工", "年度總出貨次數除以年度延遲出貨次數", "目標", "出貨達交率達100%", "", "", "", "", "", "", "", "", "", "", "", ""],
            ["1", "品質穩定", "出貨時間穩定", "管理部", "資材課員工", "年度總出貨次數除以年度延遲出貨次數", "實績", "100%", "", "", "", "", "", "", "", "", "", "", "", ""],
            ["1", "品質穩定", "出貨時間穩定", "管理部", "資材課員工", "年度總出貨次數除以年度延遲出貨次數", "判定", "目前出貨達交率皆符合標準", "", "", "", "", "", "", "", "", "", "", "", ""],
        ]
        for row_idx, values in enumerate(rows):
            for col_idx, value in enumerate(values):
                table.rows[row_idx].cells[col_idx].text = value
        doc.save(objective_path)

        with mock.patch.object(server, "BURLAN_OBJECTIVE_DIR", objective_dir):
            response = self.client.get("/api/burlan/quality-objectives")

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["achievement_rate"], 100)
        self.assertEqual(payload["year"], "115")
        self.assertEqual(payload["source_path"], str(objective_path))
        self.assertEqual(payload["items"][0]["objective"], "出貨時間穩定")
        self.assertEqual(payload["items"][0]["latest_target"], "出貨達交率達100%")
        self.assertEqual(payload["items"][0]["latest_actual"], "100%")
        self.assertEqual(payload["items"][0]["status"], "achieved")

    def test_supplier_records_load_burlan_satisfaction_list(self):
        supplier_dir = Path(self.temp_dir.name) / "supplier_module"
        (supplier_dir / "記錄").mkdir(parents=True)
        third_level_dir = Path(self.temp_dir.name) / "third_level"
        third_level_dir.mkdir()
        (third_level_dir / "供應商滿意度清單(114年度).xls").write_bytes(b"placeholder")

        mock_rows = [
            ["柏連企業股份有限公司", "", "", "", "", "", "", ""],
            ["供應商滿意度清單", "", "", "", "", "", "", ""],
            ["客戶", "服務態度", "交期配合", "品質狀況", "不良對策努力度", "事務性配合", "平均", "評定"],
            ["良器", "滿意", "非常滿意", "滿意", "滿意", "滿意", "95", "滿意"],
            ["于正瓶罐", "普通", "普通", "滿意", "滿意", "普通", "85", "普通"],
            ["說  明", "非常滿意—100， 滿意—80", "", "", "", "", "", ""],
        ]

        with (
            mock.patch.object(server, "BURLAN_SUPPLIER_DIR", supplier_dir),
            mock.patch.object(server, "BURLAN_THIRD_LEVEL_DIR", third_level_dir),
            mock.patch.object(server, "_read_supplier_satisfaction_xls_rows", return_value=mock_rows),
        ):
            payload = server.load_burlan_supplier_records()

        self.assertEqual(payload["count"], 2)
        self.assertIn("年度供應商滿意度清單", payload["message"])
        target = next(item for item in payload["items"] if item["name"] == "于正瓶罐")
        self.assertEqual(target["lastEvalDate"], "2025-12-31")
        self.assertEqual(target["evalScore"], 85)
        self.assertEqual(target["evalResult"], "普通")
        self.assertIn("服務態度：普通", target["issues"])
        self.assertIn("交期配合：普通", target["issues"])

    def test_audit_plan_linked_nonconformance_summary_updates(self):
        save_plan_response = self.client.post(
            "/api/audit-plans",
            json={
                "record": {
                    "id": "IA-2026-99",
                    "year": 2026,
                    "period": "上半年",
                    "scheduledDate": "2026-03-20",
                    "dept": "品管課",
                    "scope": "MP-17,MP-20",
                    "auditor": "測試稽核員",
                    "auditee": "測試受稽人",
                    "status": "已完成",
                    "actualDate": "2026-03-20",
                    "findings": 1,
                    "ncCount": 0,
                }
            },
        )
        self.assertEqual(save_plan_response.status_code, 200)
        saved_plan = next(item for item in save_plan_response.get_json()["items"] if item["id"] == "IA-2026-99")
        self.assertEqual(saved_plan["linkedNcCount"], 0)

        create_nc_response = self.client.post(
            "/api/nonconformances",
            json={
                "record": {
                    "id": "NC-2026-900",
                    "date": "2026-03-21",
                    "dept": "品管課",
                    "type": "文件不符",
                    "description": "測試關聯不符合",
                    "severity": "中度",
                    "responsible": "王小明",
                    "dueDate": "2026-03-25",
                    "status": "待處理",
                    "sourceAuditPlanId": "IA-2026-99",
                }
            },
        )
        self.assertEqual(create_nc_response.status_code, 200)
        linked_plan = next(item for item in create_nc_response.get_json()["audit_plans"] if item["id"] == "IA-2026-99")
        self.assertEqual(linked_plan["linkedNcCount"], 1)
        self.assertEqual(linked_plan["openLinkedNcCount"], 1)
        self.assertEqual(linked_plan["closedLinkedNcCount"], 0)

        close_nc_response = self.client.post(
            "/api/nonconformances",
            json={
                "record": {
                    "id": "NC-2026-900",
                    "date": "2026-03-21",
                    "dept": "品管課",
                    "type": "文件不符",
                    "description": "測試關聯不符合",
                    "severity": "中度",
                    "responsible": "王小明",
                    "dueDate": "2026-03-25",
                    "status": "已關閉",
                    "closeDate": "2026-03-26",
                    "sourceAuditPlanId": "IA-2026-99",
                }
            },
        )
        self.assertEqual(close_nc_response.status_code, 200)
        closed_plan = next(item for item in close_nc_response.get_json()["audit_plans"] if item["id"] == "IA-2026-99")
        self.assertEqual(closed_plan["linkedNcCount"], 1)
        self.assertEqual(closed_plan["openLinkedNcCount"], 0)
        self.assertEqual(closed_plan["closedLinkedNcCount"], 1)
        self.assertEqual(closed_plan["latestLinkedNcCloseDate"], "2026-03-26")


