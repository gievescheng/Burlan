"""Tests for Training (ISO 9001:2015 §7.2 能力/訓練)."""
from __future__ import annotations

from datetime import date

from erp_qms_core.repositories import document as doc_repo
from erp_qms_core.repositories import training as tr_repo


# ── TrainingCourse Repository ──────────────────────────

class TestTrainingCourseRepository:
    def test_create_and_get(self, db_session):
        course = tr_repo.create_course(db_session, {
            "course_no": "TR-ISO-01",
            "title": "ISO 9001 意識訓練",
            "category": "iso_awareness",
            "duration_hours": 8.0,
            "validity_months": 24,
            "passing_score": 70.0,
        })
        db_session.flush()
        assert course.course_no == "TR-ISO-01"
        assert course.status == "active"
        assert course.validity_months == 24

    def test_filter_by_category(self, db_session):
        tr_repo.create_course(db_session, {
            "course_no": "TR-SAFE", "title": "安全", "category": "safety",
        })
        tr_repo.create_course(db_session, {
            "course_no": "TR-QA", "title": "品質", "category": "quality",
        })
        db_session.flush()
        safety = tr_repo.list_courses(db_session, category="safety")
        assert len(safety) == 1


# ── TrainingRecord Repository ──────────────────────────

class TestTrainingRecordRepository:
    def test_create_record(self, db_session):
        course = tr_repo.create_course(db_session, {
            "course_no": "TR-01", "title": "測試課程", "passing_score": 60.0,
        })
        db_session.flush()
        record = tr_repo.create_record(db_session, {
            "record_no": "REC-001",
            "course_id": course.id,
            "employee_id": "EMP-001",
            "employee_name": "王小明",
            "department": "Production",
            "score": 85.0,
            "passed": True,
        })
        db_session.flush()
        assert record.record_no == "REC-001"
        assert record.passed is True

    def test_filter_by_employee(self, db_session):
        course = tr_repo.create_course(db_session, {
            "course_no": "TR-02", "title": "課程2",
        })
        db_session.flush()
        tr_repo.create_record(db_session, {
            "record_no": "R1", "course_id": course.id,
            "employee_id": "EMP-A",
        })
        tr_repo.create_record(db_session, {
            "record_no": "R2", "course_id": course.id,
            "employee_id": "EMP-B",
        })
        db_session.flush()
        recs = tr_repo.list_records(db_session, employee_id="EMP-A")
        assert len(recs) == 1


# ── TrainingCourse API ─────────────────────────────────

class TestTrainingCourseAPI:
    def test_create_course(self, client):
        r = client.post("/api/erp/training-courses", json={
            "course_no": "TR-API-01",
            "title": "ISO 9001 意識",
            "category": "iso_awareness",
            "duration_hours": 4,
            "validity_months": 12,
            "passing_score": 70,
        })
        assert r.status_code == 201, r.text
        assert r.json()["course_no"] == "TR-API-01"

    def test_invalid_category_422(self, client):
        r = client.post("/api/erp/training-courses", json={
            "course_no": "BAD-01", "category": "unknown",
        })
        assert r.status_code == 422

    def test_duplicate_course_no_409(self, client):
        client.post("/api/erp/training-courses", json={"course_no": "DUP-TR"})
        r = client.post("/api/erp/training-courses", json={"course_no": "DUP-TR"})
        assert r.status_code == 409

    def test_course_linked_to_document(self, client):
        # 先建立 SOP 文件
        doc = client.post("/api/erp/documents", json={
            "document_no": "WI-TR-01", "title": "訓練教材",
            "category": "work_instruction",
        }).json()
        # 連結課程
        r = client.post("/api/erp/training-courses", json={
            "course_no": "TR-LINKED-01",
            "title": "連結文件的課程",
            "related_document_id": doc["id"],
        })
        assert r.status_code == 201
        assert r.json()["related_document_id"] == doc["id"]

    def test_course_linked_to_missing_document(self, client):
        r = client.post("/api/erp/training-courses", json={
            "course_no": "TR-BAD-LINK",
            "related_document_id": "nonexistent",
        })
        assert r.status_code == 422

    def test_update_status_archive(self, client):
        c = client.post("/api/erp/training-courses", json={
            "course_no": "TR-ARC", "title": "待封存",
        }).json()
        r = client.patch(f"/api/erp/training-courses/{c['id']}", json={
            "status": "archived",
        })
        assert r.status_code == 200
        assert r.json()["status"] == "archived"


# ── TrainingRecord API ─────────────────────────────────

class TestTrainingRecordAPI:
    def _make_course(self, client, passing=70.0, validity_months=12):
        return client.post("/api/erp/training-courses", json={
            "course_no": "TR-REC-COURSE",
            "title": "測試課程",
            "passing_score": passing,
            "validity_months": validity_months,
        }).json()

    def test_create_record(self, client):
        course = self._make_course(client)
        r = client.post("/api/erp/training-records", json={
            "record_no": "REC-API-01",
            "course_id": course["id"],
            "employee_id": "EMP-001",
            "employee_name": "王小明",
            "department": "Production",
            "score": 85,
            "completed_date": str(date(2026, 4, 14)),
        })
        assert r.status_code == 201, r.text
        body = r.json()
        assert body["passed"] is True
        # 自動計算到期日：2026-04-14 + 12 months = 2027-04-14
        assert body["expiry_date"] == "2027-04-14"

    def test_auto_judge_fail(self, client):
        """分數低於 passing_score 自動判為不合格"""
        course = self._make_course(client, passing=70.0)
        r = client.post("/api/erp/training-records", json={
            "record_no": "REC-FAIL",
            "course_id": course["id"],
            "employee_id": "EMP-002",
            "score": 50,
            "completed_date": str(date(2026, 4, 14)),
        })
        assert r.status_code == 201
        body = r.json()
        assert body["passed"] is False
        # 不合格不自動填到期日
        assert body["expiry_date"] is None

    def test_no_expiry_when_validity_zero(self, client):
        """validity_months=0 (永久有效) 不自動填到期日"""
        course = client.post("/api/erp/training-courses", json={
            "course_no": "TR-PERM", "title": "永久有效",
            "validity_months": 0, "passing_score": 60,
        }).json()
        r = client.post("/api/erp/training-records", json={
            "record_no": "REC-PERM",
            "course_id": course["id"],
            "employee_id": "EMP-003",
            "score": 90,
            "completed_date": str(date(2026, 4, 14)),
        })
        assert r.status_code == 201
        assert r.json()["passed"] is True
        assert r.json()["expiry_date"] is None

    def test_update_score_recomputes_pass(self, client):
        """更新分數應重算 passed 與到期日"""
        course = self._make_course(client, passing=70.0)
        rec = client.post("/api/erp/training-records", json={
            "record_no": "REC-UPD",
            "course_id": course["id"],
            "employee_id": "EMP-004",
            "score": 50,
            "completed_date": str(date(2026, 4, 14)),
        }).json()
        assert rec["passed"] is False
        r = client.patch(f"/api/erp/training-records/{rec['id']}", json={
            "score": 90,
        })
        assert r.status_code == 200
        assert r.json()["passed"] is True
        assert r.json()["expiry_date"] == "2027-04-14"

    def test_invalid_training_type_422(self, client):
        course = self._make_course(client)
        r = client.post("/api/erp/training-records", json={
            "record_no": "REC-BAD", "course_id": course["id"],
            "employee_id": "EMP-X", "training_type": "telepathy",
        })
        assert r.status_code == 422

    def test_record_for_missing_course(self, client):
        r = client.post("/api/erp/training-records", json={
            "record_no": "REC-NO-COURSE",
            "course_id": "nonexistent",
            "employee_id": "EMP-Y",
        })
        assert r.status_code == 422

    def test_duplicate_record_no_409(self, client):
        course = self._make_course(client)
        client.post("/api/erp/training-records", json={
            "record_no": "REC-DUP", "course_id": course["id"],
            "employee_id": "EMP-Z",
        })
        r = client.post("/api/erp/training-records", json={
            "record_no": "REC-DUP", "course_id": course["id"],
            "employee_id": "EMP-Z2",
        })
        assert r.status_code == 409

    def test_filter_records_by_department(self, client):
        course = self._make_course(client)
        client.post("/api/erp/training-records", json={
            "record_no": "REC-D1", "course_id": course["id"],
            "employee_id": "E1", "department": "Production",
        })
        client.post("/api/erp/training-records", json={
            "record_no": "REC-D2", "course_id": course["id"],
            "employee_id": "E2", "department": "QA",
        })
        r = client.get("/api/erp/training-records?department=QA")
        assert r.status_code == 200
        assert len(r.json()) == 1
        assert r.json()[0]["department"] == "QA"
