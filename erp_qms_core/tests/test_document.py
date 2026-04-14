"""Tests for Document Control (ISO 9001:2015 §7.5)."""
from __future__ import annotations

from datetime import date

from erp_qms_core.domain.transitions import validate_status_transition
from erp_qms_core.repositories import document as doc_repo


# ── Domain transitions ─────────────────────────────────

class TestDocumentRevisionTransitions:
    def test_draft_to_under_review(self):
        assert validate_status_transition(
            "document_revision", "draft", "under_review",
        ) is None

    def test_under_review_back_to_draft(self):
        # 審查未過可退回草稿修訂
        assert validate_status_transition(
            "document_revision", "under_review", "draft",
        ) is None

    def test_under_review_to_approved(self):
        assert validate_status_transition(
            "document_revision", "under_review", "approved",
        ) is None

    def test_draft_to_approved_blocked(self):
        # 不可跳過審查直接核准
        err = validate_status_transition(
            "document_revision", "draft", "approved",
        )
        assert err is not None

    def test_approved_to_effective(self):
        assert validate_status_transition(
            "document_revision", "approved", "effective",
        ) is None

    def test_effective_to_superseded(self):
        assert validate_status_transition(
            "document_revision", "effective", "superseded",
        ) is None

    def test_effective_to_obsolete(self):
        assert validate_status_transition(
            "document_revision", "effective", "obsolete",
        ) is None

    def test_obsolete_is_terminal(self):
        err = validate_status_transition(
            "document_revision", "obsolete", "effective",
        )
        assert err is not None


# ── Document Repository ────────────────────────────────

class TestDocumentRepository:
    def test_create_and_get(self, db_session):
        doc = doc_repo.create_document(db_session, {
            "document_no": "QP-01",
            "title": "文件管理程序",
            "category": "procedure",
            "classification": "controlled",
            "owner": "QA Manager",
            "department": "QA",
        })
        db_session.flush()
        assert doc.document_no == "QP-01"
        assert doc.status == "active"

    def test_filter_by_category(self, db_session):
        doc_repo.create_document(db_session, {
            "document_no": "QM-01", "title": "品質手冊", "category": "manual",
        })
        doc_repo.create_document(db_session, {
            "document_no": "QP-02", "title": "稽核程序", "category": "procedure",
        })
        db_session.flush()
        manuals = doc_repo.list_documents(db_session, category="manual")
        assert len(manuals) == 1
        assert manuals[0].document_no == "QM-01"

    def test_filter_by_department(self, db_session):
        doc_repo.create_document(db_session, {
            "document_no": "PD-01", "title": "生產 SOP", "department": "Production",
        })
        doc_repo.create_document(db_session, {
            "document_no": "QA-01", "title": "檢驗 SOP", "department": "QA",
        })
        db_session.flush()
        qa_docs = doc_repo.list_documents(db_session, department="QA")
        assert len(qa_docs) == 1


# ── DocumentRevision Repository ────────────────────────

class TestDocumentRevisionRepository:
    def test_create_revision(self, db_session):
        doc = doc_repo.create_document(db_session, {
            "document_no": "QP-01", "title": "文件管理程序",
        })
        db_session.flush()
        rev = doc_repo.create_revision(db_session, {
            "document_id": doc.id,
            "revision": "A",
            "change_summary": "初版建立",
            "prepared_by": "author1",
        })
        db_session.flush()
        assert rev.revision == "A"
        assert rev.status == "draft"
        assert rev.is_current is False

    def test_filter_revisions_by_document(self, db_session):
        doc1 = doc_repo.create_document(db_session, {
            "document_no": "QP-01", "title": "文件管理程序",
        })
        doc2 = doc_repo.create_document(db_session, {
            "document_no": "QP-02", "title": "其他程序",
        })
        db_session.flush()
        doc_repo.create_revision(db_session, {
            "document_id": doc1.id, "revision": "A",
        })
        doc_repo.create_revision(db_session, {
            "document_id": doc1.id, "revision": "B",
        })
        doc_repo.create_revision(db_session, {
            "document_id": doc2.id, "revision": "A",
        })
        db_session.flush()
        revs = doc_repo.list_revisions(db_session, document_id=doc1.id)
        assert len(revs) == 2


# ── Document API ───────────────────────────────────────

class TestDocumentAPI:
    def test_create_document(self, client):
        r = client.post("/api/erp/documents", json={
            "document_no": "QP-API-01",
            "title": "API 測試文件",
            "category": "procedure",
            "owner": "author1",
        })
        assert r.status_code == 201, r.text
        assert r.json()["document_no"] == "QP-API-01"

    def test_invalid_category_422(self, client):
        r = client.post("/api/erp/documents", json={
            "document_no": "BAD-01",
            "category": "unknown_category",
        })
        assert r.status_code == 422

    def test_invalid_classification_422(self, client):
        r = client.post("/api/erp/documents", json={
            "document_no": "BAD-02",
            "classification": "super_secret",
        })
        assert r.status_code == 422

    def test_duplicate_document_no_409(self, client):
        r1 = client.post("/api/erp/documents", json={
            "document_no": "DUP-01", "title": "第一版",
        })
        assert r1.status_code == 201
        r2 = client.post("/api/erp/documents", json={
            "document_no": "DUP-01", "title": "重複",
        })
        assert r2.status_code == 409


# ── DocumentRevision API ───────────────────────────────

class TestDocumentRevisionAPI:
    def _create_doc(self, client, no="QP-REV"):
        r = client.post("/api/erp/documents", json={
            "document_no": no, "title": "測試文件",
        })
        return r.json()["id"]

    def test_full_lifecycle(self, client):
        """完整生命週期：draft → under_review → approved → effective"""
        doc_id = self._create_doc(client)
        r = client.post("/api/erp/document-revisions", json={
            "document_id": doc_id,
            "revision": "A",
            "change_summary": "初版",
            "prepared_by": "author1",
        })
        assert r.status_code == 201
        rev_id = r.json()["id"]

        # draft → under_review
        r2 = client.patch(f"/api/erp/document-revisions/{rev_id}", json={
            "status": "under_review",
            "reviewed_by": "reviewer1",
        })
        assert r2.status_code == 200, r2.text

        # under_review → approved（需同時有 reviewed_by + approved_by）
        r3 = client.patch(f"/api/erp/document-revisions/{rev_id}", json={
            "status": "approved",
            "approved_by": "manager1",
        })
        assert r3.status_code == 200, r3.text
        assert r3.json()["approved_by"] == "manager1"
        assert r3.json()["approved_at"] is not None  # 自動填時間戳

        # approved → effective
        r4 = client.patch(f"/api/erp/document-revisions/{rev_id}", json={
            "status": "effective",
            "effective_date": str(date(2026, 4, 14)),
        })
        assert r4.status_code == 200, r4.text
        assert r4.json()["is_current"] is True

        # 主檔 current_revision 同步更新
        doc = client.get(f"/api/erp/documents/{doc_id}").json()
        assert doc["current_revision"] == "A"

    def test_approve_without_reviewer_blocked(self, client):
        """ISO §7.5.2 b) — 核准前必須有審查紀錄"""
        doc_id = self._create_doc(client, "QP-NO-REV")
        rev = client.post("/api/erp/document-revisions", json={
            "document_id": doc_id, "revision": "A",
        }).json()
        # draft → under_review 但未填 reviewed_by
        client.patch(f"/api/erp/document-revisions/{rev['id']}", json={
            "status": "under_review",
        })
        # under_review → approved（未填 reviewed_by / approved_by 應被擋）
        r = client.patch(f"/api/erp/document-revisions/{rev['id']}", json={
            "status": "approved",
        })
        assert r.status_code == 422
        assert "reviewed_by" in r.text or "approved_by" in r.text

    def test_skip_approval_blocked(self, client):
        """不可從 draft 直接跳到 approved"""
        doc_id = self._create_doc(client, "QP-SKIP")
        rev = client.post("/api/erp/document-revisions", json={
            "document_id": doc_id, "revision": "A",
        }).json()
        r = client.patch(f"/api/erp/document-revisions/{rev['id']}", json={
            "status": "approved",
        })
        assert r.status_code == 422

    def test_new_effective_supersedes_old(self, client):
        """新版本 effective 時，舊 effective 自動變 superseded"""
        doc_id = self._create_doc(client, "QP-SUP")

        # 建立並發行 A 版
        rev_a = client.post("/api/erp/document-revisions", json={
            "document_id": doc_id, "revision": "A", "prepared_by": "a",
        }).json()
        client.patch(f"/api/erp/document-revisions/{rev_a['id']}",
                     json={"status": "under_review", "reviewed_by": "r"})
        client.patch(f"/api/erp/document-revisions/{rev_a['id']}",
                     json={"status": "approved", "approved_by": "m"})
        client.patch(f"/api/erp/document-revisions/{rev_a['id']}",
                     json={"status": "effective"})

        # 建立並發行 B 版
        rev_b = client.post("/api/erp/document-revisions", json={
            "document_id": doc_id, "revision": "B", "prepared_by": "a",
        }).json()
        client.patch(f"/api/erp/document-revisions/{rev_b['id']}",
                     json={"status": "under_review", "reviewed_by": "r"})
        client.patch(f"/api/erp/document-revisions/{rev_b['id']}",
                     json={"status": "approved", "approved_by": "m"})
        client.patch(f"/api/erp/document-revisions/{rev_b['id']}",
                     json={"status": "effective"})

        # A 版應自動轉為 superseded 且 is_current=False
        rev_a_final = client.get(f"/api/erp/document-revisions/{rev_a['id']}").json()
        assert rev_a_final["status"] == "superseded"
        assert rev_a_final["is_current"] is False

        # B 版應為 effective 且 is_current=True
        rev_b_final = client.get(f"/api/erp/document-revisions/{rev_b['id']}").json()
        assert rev_b_final["status"] == "effective"
        assert rev_b_final["is_current"] is True

        # 主檔指向 B 版
        doc = client.get(f"/api/erp/documents/{doc_id}").json()
        assert doc["current_revision"] == "B"

    def test_duplicate_revision_409(self, client):
        doc_id = self._create_doc(client, "QP-DUP-REV")
        r1 = client.post("/api/erp/document-revisions", json={
            "document_id": doc_id, "revision": "A",
        })
        assert r1.status_code == 201
        r2 = client.post("/api/erp/document-revisions", json={
            "document_id": doc_id, "revision": "A",
        })
        assert r2.status_code == 409

    def test_revision_for_missing_document(self, client):
        r = client.post("/api/erp/document-revisions", json={
            "document_id": "nonexistent-id", "revision": "A",
        })
        assert r.status_code == 422
