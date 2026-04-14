"""Tests for Internal Audit (ISO 9001:2015 §9.2)."""
from __future__ import annotations

from datetime import date

from erp_qms_core.domain.transitions import validate_status_transition
from erp_qms_core.repositories import audit as audit_repo
from erp_qms_core.repositories import capa as capa_repo


# ── Domain transitions ─────────────────────────────────

class TestAuditTransitions:
    def test_planned_to_in_progress(self):
        assert validate_status_transition(
            "internal_audit", "planned", "in_progress",
        ) is None

    def test_skip_to_closed_blocked(self):
        err = validate_status_transition(
            "internal_audit", "planned", "closed",
        )
        assert err is not None

    def test_reporting_to_closed(self):
        assert validate_status_transition(
            "internal_audit", "reporting", "closed",
        ) is None

    def test_reporting_can_reopen_to_in_progress(self):
        assert validate_status_transition(
            "internal_audit", "reporting", "in_progress",
        ) is None

    def test_closed_is_terminal(self):
        err = validate_status_transition(
            "internal_audit", "closed", "planned",
        )
        assert err is not None


class TestFindingTransitions:
    def test_open_to_corrective_action(self):
        assert validate_status_transition(
            "audit_finding", "open", "corrective_action",
        ) is None

    def test_corrective_to_verified(self):
        assert validate_status_transition(
            "audit_finding", "corrective_action", "verified",
        ) is None

    def test_verified_to_closed(self):
        assert validate_status_transition(
            "audit_finding", "verified", "closed",
        ) is None

    def test_corrective_can_reopen(self):
        """改善不足可退回 open"""
        assert validate_status_transition(
            "audit_finding", "corrective_action", "open",
        ) is None

    def test_verified_can_reopen_to_corrective(self):
        assert validate_status_transition(
            "audit_finding", "verified", "corrective_action",
        ) is None


# ── Audit Repository ───────────────────────────────────

class TestAuditRepository:
    def test_create_audit(self, db_session):
        a = audit_repo.create_audit(db_session, {
            "audit_no": "IA-2026-01",
            "audit_type": "planned",
            "scope": "process",
            "audit_criteria": "ISO 9001:2015 §8.5, §8.6",
            "department": "Production",
            "lead_auditor": "QM-01",
        })
        db_session.flush()
        assert a.audit_no == "IA-2026-01"
        assert a.status == "planned"
        assert a.total_findings == 0

    def test_filter_by_department(self, db_session):
        audit_repo.create_audit(db_session, {
            "audit_no": "IA-P1", "department": "Production",
        })
        audit_repo.create_audit(db_session, {
            "audit_no": "IA-Q1", "department": "QA",
        })
        db_session.flush()
        prod = audit_repo.list_audits(db_session, department="Production")
        assert len(prod) == 1

    def test_recompute_counts(self, db_session):
        a = audit_repo.create_audit(db_session, {"audit_no": "IA-CNT"})
        db_session.flush()
        audit_repo.create_finding(db_session, {
            "finding_no": "F-1", "audit_id": a.id, "finding_type": "major_nc",
        })
        audit_repo.create_finding(db_session, {
            "finding_no": "F-2", "audit_id": a.id, "finding_type": "minor_nc",
        })
        audit_repo.create_finding(db_session, {
            "finding_no": "F-3", "audit_id": a.id, "finding_type": "observation",
        })
        db_session.flush()
        audit_repo.recompute_audit_counts(db_session, a.id)
        refreshed = audit_repo.get_audit(db_session, a.id)
        assert refreshed.total_findings == 3
        assert refreshed.major_findings_count == 1
        assert refreshed.minor_findings_count == 1
        assert refreshed.observation_count == 1


# ── Audit API ──────────────────────────────────────────

class TestAuditAPI:
    def test_create_audit(self, client):
        r = client.post("/api/erp/audits", json={
            "audit_no": "IA-API-01",
            "audit_type": "planned",
            "scope": "process",
            "audit_criteria": "ISO 9001:2015 §9.2",
            "department": "QA",
            "lead_auditor": "Manager-A",
            "planned_start_date": "2026-05-01",
            "planned_end_date": "2026-05-03",
        })
        assert r.status_code == 201, r.text
        assert r.json()["audit_no"] == "IA-API-01"
        assert r.json()["status"] == "planned"

    def test_invalid_audit_type_422(self, client):
        r = client.post("/api/erp/audits", json={
            "audit_no": "IA-BAD", "audit_type": "surprise_visit",
        })
        assert r.status_code == 422

    def test_invalid_scope_422(self, client):
        r = client.post("/api/erp/audits", json={
            "audit_no": "IA-BAD2", "scope": "whole_company",
        })
        assert r.status_code == 422

    def test_duplicate_audit_no_409(self, client):
        client.post("/api/erp/audits", json={"audit_no": "IA-DUP"})
        r = client.post("/api/erp/audits", json={"audit_no": "IA-DUP"})
        assert r.status_code == 409

    def test_audit_lifecycle(self, client):
        audit = client.post("/api/erp/audits", json={
            "audit_no": "IA-LIFE", "department": "Production",
        }).json()
        # planned → in_progress
        r = client.patch(f"/api/erp/audits/{audit['id']}", json={
            "status": "in_progress",
            "actual_start_date": "2026-05-01",
        })
        assert r.status_code == 200
        # in_progress → reporting
        r = client.patch(f"/api/erp/audits/{audit['id']}", json={
            "status": "reporting",
            "actual_end_date": "2026-05-03",
            "report_summary": "3 minor NC found",
        })
        assert r.status_code == 200
        # reporting → closed
        r = client.patch(f"/api/erp/audits/{audit['id']}", json={
            "status": "closed",
            "closed_by": "MR",
            "conclusion": "All findings closed",
        })
        assert r.status_code == 200

    def test_cannot_close_audit_with_open_findings(self, client):
        """ISO §9.2.2 e) — 稽核結案前所有發現必須已關閉"""
        audit = client.post("/api/erp/audits", json={
            "audit_no": "IA-OPEN", "department": "QA",
        }).json()
        # 建立一個 open finding
        finding = client.post("/api/erp/audit-findings", json={
            "finding_no": "F-OPEN", "audit_id": audit["id"],
            "finding_type": "minor_nc", "description": "發現事實",
        }).json()
        client.patch(f"/api/erp/audits/{audit['id']}",
                     json={"status": "in_progress"})
        client.patch(f"/api/erp/audits/{audit['id']}",
                     json={"status": "reporting"})
        # 試圖關閉 audit（應被擋）
        r = client.patch(f"/api/erp/audits/{audit['id']}",
                         json={"status": "closed"})
        assert r.status_code == 422
        assert "finding(s) still open" in r.text

        # 先關閉 finding
        client.patch(f"/api/erp/audit-findings/{finding['id']}",
                     json={"status": "corrective_action"})
        client.patch(f"/api/erp/audit-findings/{finding['id']}",
                     json={"status": "verified", "verified_by": "QM"})
        client.patch(f"/api/erp/audit-findings/{finding['id']}",
                     json={"status": "closed"})

        # 現在可以關閉 audit
        r = client.patch(f"/api/erp/audits/{audit['id']}",
                         json={"status": "closed"})
        assert r.status_code == 200


# ── Finding API ────────────────────────────────────────

class TestFindingAPI:
    def _make_audit(self, client, no="IA-F"):
        return client.post("/api/erp/audits", json={"audit_no": no}).json()

    def test_create_finding(self, client):
        audit = self._make_audit(client)
        r = client.post("/api/erp/audit-findings", json={
            "finding_no": "F-01", "audit_id": audit["id"],
            "clause": "7.5.2", "finding_type": "minor_nc",
            "description": "程序書未依規定編碼",
            "evidence": "檢視 QP-01 A 版未顯示審查簽署",
        })
        assert r.status_code == 201
        assert r.json()["clause"] == "7.5.2"

    def test_major_nc_auto_requires_capa(self, client):
        """major_nc 自動觸發 requires_capa"""
        audit = self._make_audit(client, "IA-MAJ")
        r = client.post("/api/erp/audit-findings", json={
            "finding_no": "F-MAJ", "audit_id": audit["id"],
            "finding_type": "major_nc",
            "description": "重大不符合",
        })
        assert r.status_code == 201
        assert r.json()["requires_capa"] is True

    def test_invalid_finding_type_422(self, client):
        audit = self._make_audit(client, "IA-BAD")
        r = client.post("/api/erp/audit-findings", json={
            "finding_no": "F-BAD", "audit_id": audit["id"],
            "finding_type": "nonsense",
        })
        assert r.status_code == 422

    def test_finding_for_missing_audit(self, client):
        r = client.post("/api/erp/audit-findings", json={
            "finding_no": "F-ORPH", "audit_id": "nonexistent",
        })
        assert r.status_code == 422

    def test_cannot_close_finding_without_verification(self, client):
        """ISO §9.2.2 e) — 關閉發現必須先驗證"""
        audit = self._make_audit(client, "IA-VER")
        finding = client.post("/api/erp/audit-findings", json={
            "finding_no": "F-VER", "audit_id": audit["id"],
            "finding_type": "minor_nc", "description": "need improvement",
        }).json()
        client.patch(f"/api/erp/audit-findings/{finding['id']}",
                     json={"status": "corrective_action"})
        # verified 需要 verified_by
        client.patch(f"/api/erp/audit-findings/{finding['id']}",
                     json={"status": "verified"})
        # 嘗試 close 但沒有 verified_by（此路徑故意省略）
        # 直接 verified → closed 沒 verified_by 設值應被擋
        r = client.patch(f"/api/erp/audit-findings/{finding['id']}",
                         json={"status": "closed"})
        assert r.status_code == 422

    def test_link_finding_to_capa(self, client, db_session):
        """發現可連結至 CAPA"""
        # 直接在 db 建立 CAPA（跨 session 需用 client 建立的 TestClient app）
        audit = self._make_audit(client, "IA-LINK")
        capa_resp = client.post("/api/erp/capas", json={
            "capa_no": "CAPA-FL-01", "subject": "matching finding",
            "source_type": "audit",
        })
        assert capa_resp.status_code == 201
        capa_id = capa_resp.json()["id"]

        r = client.post("/api/erp/audit-findings", json={
            "finding_no": "F-LINK", "audit_id": audit["id"],
            "finding_type": "major_nc",
            "description": "link to capa",
            "capa_id": capa_id,
        })
        assert r.status_code == 201
        assert r.json()["capa_id"] == capa_id

    def test_link_finding_to_missing_capa(self, client):
        audit = self._make_audit(client, "IA-LINKBAD")
        r = client.post("/api/erp/audit-findings", json={
            "finding_no": "F-LINKBAD", "audit_id": audit["id"],
            "capa_id": "nonexistent-capa",
        })
        assert r.status_code == 422

    def test_audit_counts_recomputed_on_finding_change(self, client):
        """新增/變更/刪除發現時，稽核主檔統計欄位自動同步"""
        audit = self._make_audit(client, "IA-COUNT")
        client.post("/api/erp/audit-findings", json={
            "finding_no": "FC-1", "audit_id": audit["id"],
            "finding_type": "major_nc", "description": "x",
        })
        client.post("/api/erp/audit-findings", json={
            "finding_no": "FC-2", "audit_id": audit["id"],
            "finding_type": "minor_nc", "description": "y",
        })
        a = client.get(f"/api/erp/audits/{audit['id']}").json()
        assert a["total_findings"] == 2
        assert a["major_findings_count"] == 1
        assert a["minor_findings_count"] == 1

        # 將 minor 變更為 observation
        f2 = client.get(
            f"/api/erp/audit-findings?audit_id={audit['id']}"
        ).json()
        minor_id = next(f["id"] for f in f2 if f["finding_type"] == "minor_nc")
        client.patch(f"/api/erp/audit-findings/{minor_id}",
                     json={"finding_type": "observation"})
        a2 = client.get(f"/api/erp/audits/{audit['id']}").json()
        assert a2["minor_findings_count"] == 0
        assert a2["observation_count"] == 1

    def test_filter_findings_by_requires_capa(self, client):
        audit = self._make_audit(client, "IA-FILT")
        client.post("/api/erp/audit-findings", json={
            "finding_no": "FF-1", "audit_id": audit["id"],
            "finding_type": "major_nc", "description": "m",
        })
        client.post("/api/erp/audit-findings", json={
            "finding_no": "FF-2", "audit_id": audit["id"],
            "finding_type": "observation", "description": "o",
        })
        r = client.get(
            f"/api/erp/audit-findings?audit_id={audit['id']}&requires_capa=true"
        )
        assert r.status_code == 200
        assert len(r.json()) == 1
