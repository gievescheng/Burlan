"""Tests for CAPA + Customer Complaint (ISO 9001:2015 §10.2 + §9.1.2)."""
from __future__ import annotations

from erp_qms_core.domain.transitions import validate_status_transition
from erp_qms_core.repositories import capa as capa_repo
from erp_qms_core.repositories import master as master_repo
from erp_qms_core.repositories import nonconformance as ncr_repo
from erp_qms_core.repositories import order as order_repo


# ── helpers ────────────────────────────────────────────

def _make_prereqs(session):
    cust = master_repo.create_customer(session, {"customer_code": "C001", "name": "Acme"})
    prod = master_repo.create_product(session, {"product_code": "P001", "name": "Widget"})
    session.flush()
    return cust, prod


# ── Domain transitions ─────────────────────────────────

class TestComplaintTransitions:
    def test_received_to_under_investigation(self):
        assert validate_status_transition(
            "customer_complaint", "received", "under_investigation",
        ) is None

    def test_received_to_responding(self):
        # 簡單客訴可直接答覆
        assert validate_status_transition(
            "customer_complaint", "received", "responding",
        ) is None

    def test_received_to_closed_blocked(self):
        # 不可跳過解決直接關閉
        err = validate_status_transition("customer_complaint", "received", "closed")
        assert err is not None

    def test_resolved_to_closed(self):
        assert validate_status_transition(
            "customer_complaint", "resolved", "closed",
        ) is None

    def test_resolved_can_reopen_to_responding(self):
        # 顧客不滿可退回再答覆
        assert validate_status_transition(
            "customer_complaint", "resolved", "responding",
        ) is None

    def test_closed_is_terminal(self):
        err = validate_status_transition("customer_complaint", "closed", "received")
        assert err is not None


class TestCAPATransitions:
    def test_open_to_in_progress(self):
        assert validate_status_transition("capa", "open", "in_progress") is None

    def test_open_to_verifying_blocked(self):
        err = validate_status_transition("capa", "open", "verifying")
        assert err is not None

    def test_in_progress_to_verifying(self):
        assert validate_status_transition("capa", "in_progress", "verifying") is None

    def test_verifying_to_closed(self):
        assert validate_status_transition("capa", "verifying", "closed") is None

    def test_verifying_can_reopen(self):
        # 有效性不足可退回 in_progress
        assert validate_status_transition("capa", "verifying", "in_progress") is None

    def test_closed_is_terminal(self):
        err = validate_status_transition("capa", "closed", "open")
        assert err is not None


# ── Complaint Repository ───────────────────────────────

class TestComplaintRepository:
    def test_create_and_get(self, db_session):
        cust, prod = _make_prereqs(db_session)
        comp = capa_repo.create_complaint(db_session, {
            "complaint_no": "CMP-001",
            "customer_id": cust.id,
            "product_id": prod.id,
            "complaint_type": "quality",
            "severity": "major",
            "subject": "尺寸異常",
            "description": "客戶反映 100 PCS 中有 5 PCS 尺寸超差",
            "lot_no": "LOT-A001",
            "claimed_qty": 5,
            "channel": "email",
        })
        db_session.flush()
        assert comp.complaint_no == "CMP-001"
        assert comp.status == "received"
        assert comp.severity == "major"

    def test_filter_by_customer(self, db_session):
        cust, prod = _make_prereqs(db_session)
        capa_repo.create_complaint(db_session, {
            "complaint_no": "CMP-F1", "customer_id": cust.id, "product_id": prod.id,
        })
        capa_repo.create_complaint(db_session, {
            "complaint_no": "CMP-F2", "customer_id": cust.id, "product_id": prod.id,
        })
        db_session.flush()
        results = capa_repo.list_complaints(db_session, customer_id=cust.id)
        assert len(results) == 2

    def test_filter_by_severity_and_status(self, db_session):
        cust, prod = _make_prereqs(db_session)
        capa_repo.create_complaint(db_session, {
            "complaint_no": "CMP-S1", "customer_id": cust.id, "product_id": prod.id,
            "severity": "critical", "requires_capa": True,
        })
        capa_repo.create_complaint(db_session, {
            "complaint_no": "CMP-S2", "customer_id": cust.id, "product_id": prod.id,
            "severity": "minor",
        })
        db_session.flush()
        results = capa_repo.list_complaints(db_session, severity="critical")
        assert len(results) == 1


# ── CAPA Repository ────────────────────────────────────

class TestCAPARepository:
    def test_create_capa_from_ncr(self, db_session):
        cust, prod = _make_prereqs(db_session)
        # 先建立 SO + WO + NCR
        so = order_repo.create_sales_order(db_session, {
            "order_no": "SO-001", "customer_id": cust.id,
        })
        db_session.flush()
        wo = order_repo.create_work_order(db_session, {
            "wo_no": "WO-001", "product_id": prod.id,
            "sales_order_id": so.id, "planned_qty": 100,
        })
        db_session.flush()
        ncr = ncr_repo.create_ncr(db_session, {
            "ncr_no": "NCR-001", "work_order_id": wo.id, "product_id": prod.id,
            "severity": "critical", "requires_capa": True,
        })
        db_session.flush()
        # 建立 CAPA 並連結 NCR
        capa = capa_repo.create_capa(db_session, {
            "capa_no": "CAPA-001",
            "capa_type": "corrective",
            "source_type": "ncr",
            "ncr_id": ncr.id,
            "subject": "尺寸超差矯正措施",
            "severity": "critical",
            "root_cause_method": "5why",
            "root_cause": "刀具磨損未及時更換",
            "corrective_action": "更新刀具更換 SOP，由 8 小時改為 4 小時",
            "preventive_action": "建立刀具壽命監控系統",
            "assigned_to": "QM-01",
        })
        db_session.flush()
        assert capa.capa_no == "CAPA-001"
        assert capa.status == "open"
        assert capa.ncr_id == ncr.id

    def test_filter_by_assigned_to(self, db_session):
        capa_repo.create_capa(db_session, {
            "capa_no": "CAPA-A1", "subject": "test1", "assigned_to": "QM-01",
        })
        capa_repo.create_capa(db_session, {
            "capa_no": "CAPA-A2", "subject": "test2", "assigned_to": "QM-02",
        })
        db_session.flush()
        results = capa_repo.list_capas(db_session, assigned_to="QM-01")
        assert len(results) == 1


# ── Complaint API ──────────────────────────────────────

class TestComplaintAPI:
    def _setup(self, client):
        c = client.post("/api/erp/customers", json={"customer_code": "C001", "name": "Acme"})
        p = client.post("/api/erp/products", json={"product_code": "P001", "name": "Widget"})
        return c.json()["id"], p.json()["id"]

    def test_create_complaint(self, client):
        cid, pid = self._setup(client)
        r = client.post("/api/erp/complaints", json={
            "complaint_no": "CMP-001",
            "customer_id": cid,
            "product_id": pid,
            "complaint_type": "quality",
            "severity": "major",
            "subject": "尺寸異常",
            "lot_no": "LOT-A001",
            "claimed_qty": 5,
            "channel": "email",
        })
        assert r.status_code == 201
        body = r.json()
        assert body["complaint_no"] == "CMP-001"
        assert body["status"] == "received"
        assert body["requires_capa"] is False  # major 不強制 CAPA

    def test_critical_complaint_auto_requires_capa(self, client):
        """ISO 10.2 — 重大客訴須強制觸發 CAPA"""
        cid, pid = self._setup(client)
        r = client.post("/api/erp/complaints", json={
            "complaint_no": "CMP-CR", "customer_id": cid, "product_id": pid,
            "severity": "critical",
        })
        assert r.status_code == 201
        assert r.json()["requires_capa"] is True

    def test_complaint_lifecycle(self, client):
        cid, pid = self._setup(client)
        r = client.post("/api/erp/complaints", json={
            "complaint_no": "CMP-LP", "customer_id": cid, "product_id": pid,
        })
        comp_id = r.json()["id"]
        # received → under_investigation → responding → resolved → closed
        for target in ["under_investigation", "responding", "resolved", "closed"]:
            r = client.patch(f"/api/erp/complaints/{comp_id}", json={"status": target})
            assert r.status_code == 200, f"Failed at {target}: {r.json()}"

    def test_complaint_skip_blocked(self, client):
        cid, pid = self._setup(client)
        r = client.post("/api/erp/complaints", json={
            "complaint_no": "CMP-SK", "customer_id": cid, "product_id": pid,
        })
        comp_id = r.json()["id"]
        r = client.patch(f"/api/erp/complaints/{comp_id}", json={"status": "closed"})
        assert r.status_code == 422

    def test_invalid_complaint_type_422(self, client):
        cid, pid = self._setup(client)
        r = client.post("/api/erp/complaints", json={
            "complaint_no": "CMP-IT", "customer_id": cid, "product_id": pid,
            "complaint_type": "weird_type",
        })
        assert r.status_code == 422

    def test_invalid_channel_422(self, client):
        cid, pid = self._setup(client)
        r = client.post("/api/erp/complaints", json={
            "complaint_no": "CMP-IC", "customer_id": cid, "product_id": pid,
            "channel": "carrier_pigeon",
        })
        assert r.status_code == 422

    def test_duplicate_complaint_no_409(self, client):
        cid, pid = self._setup(client)
        client.post("/api/erp/complaints", json={
            "complaint_no": "CMP-DUP", "customer_id": cid, "product_id": pid,
        })
        r = client.post("/api/erp/complaints", json={
            "complaint_no": "CMP-DUP", "customer_id": cid, "product_id": pid,
        })
        assert r.status_code == 409

    def test_filter_complaints_requires_capa(self, client):
        cid, pid = self._setup(client)
        client.post("/api/erp/complaints", json={
            "complaint_no": "CMP-FC1", "customer_id": cid, "product_id": pid,
            "severity": "critical",  # 自動 requires_capa
        })
        client.post("/api/erp/complaints", json={
            "complaint_no": "CMP-FC2", "customer_id": cid, "product_id": pid,
            "severity": "minor",
        })
        r = client.get("/api/erp/complaints?requires_capa=true")
        assert r.status_code == 200
        assert len(r.json()) == 1


# ── CAPA API ───────────────────────────────────────────

class TestCAPAAPI:
    def _setup(self, client):
        c = client.post("/api/erp/customers", json={"customer_code": "C001", "name": "Acme"})
        p = client.post("/api/erp/products", json={"product_code": "P001", "name": "Widget"})
        return c.json()["id"], p.json()["id"]

    def test_create_capa(self, client):
        r = client.post("/api/erp/capas", json={
            "capa_no": "CAPA-001",
            "capa_type": "corrective",
            "source_type": "ncr",
            "subject": "尺寸超差矯正",
            "severity": "major",
            "root_cause_method": "5why",
            "root_cause": "刀具磨損",
            "corrective_action": "縮短刀具更換週期",
            "assigned_to": "QM-01",
        })
        assert r.status_code == 201
        body = r.json()
        assert body["capa_no"] == "CAPA-001"
        assert body["status"] == "open"
        assert body["effectiveness_verified"] is False

    def test_capa_lifecycle_with_verification(self, client):
        """ISO §10.2.1 d) — 結案前必須驗證有效性"""
        r = client.post("/api/erp/capas", json={
            "capa_no": "CAPA-LP", "subject": "test",
        })
        capa_id = r.json()["id"]
        # open → in_progress → verifying
        for target in ["in_progress", "verifying"]:
            r = client.patch(f"/api/erp/capas/{capa_id}", json={"status": target})
            assert r.status_code == 200, f"Failed at {target}"
        # 設定有效性驗證
        r = client.patch(f"/api/erp/capas/{capa_id}", json={
            "effectiveness_check": "驗證 30 天無重複發生",
            "effectiveness_verified": True,
            "verified_by": "QM-Director",
        })
        assert r.status_code == 200
        # 現在可以結案
        r = client.patch(f"/api/erp/capas/{capa_id}", json={"status": "closed"})
        assert r.status_code == 200

    def test_close_capa_without_verification_blocked(self, client):
        """ISO §10.2.1 d) — 未驗證有效性不可結案"""
        r = client.post("/api/erp/capas", json={
            "capa_no": "CAPA-NV", "subject": "test",
        })
        capa_id = r.json()["id"]
        client.patch(f"/api/erp/capas/{capa_id}", json={"status": "in_progress"})
        client.patch(f"/api/erp/capas/{capa_id}", json={"status": "verifying"})
        # 嘗試直接結案
        r = client.patch(f"/api/erp/capas/{capa_id}", json={"status": "closed"})
        assert r.status_code == 422
        assert "effectiveness_verified" in r.json()["detail"]

    def test_verifying_can_reopen(self, client):
        """有效性不足可退回 in_progress"""
        r = client.post("/api/erp/capas", json={
            "capa_no": "CAPA-RE", "subject": "test",
        })
        capa_id = r.json()["id"]
        client.patch(f"/api/erp/capas/{capa_id}", json={"status": "in_progress"})
        client.patch(f"/api/erp/capas/{capa_id}", json={"status": "verifying"})
        # 退回
        r = client.patch(f"/api/erp/capas/{capa_id}", json={"status": "in_progress"})
        assert r.status_code == 200

    def test_skip_in_progress_blocked(self, client):
        r = client.post("/api/erp/capas", json={
            "capa_no": "CAPA-SK", "subject": "test",
        })
        capa_id = r.json()["id"]
        # open → verifying 不允許
        r = client.patch(f"/api/erp/capas/{capa_id}", json={"status": "verifying"})
        assert r.status_code == 422

    def test_invalid_capa_type_422(self, client):
        r = client.post("/api/erp/capas", json={
            "capa_no": "CAPA-IT", "subject": "test",
            "capa_type": "magical",
        })
        assert r.status_code == 422

    def test_invalid_root_cause_method_422(self, client):
        r = client.post("/api/erp/capas", json={
            "capa_no": "CAPA-IR", "subject": "test",
            "root_cause_method": "ouija_board",
        })
        assert r.status_code == 422

    def test_duplicate_capa_no_409(self, client):
        client.post("/api/erp/capas", json={"capa_no": "CAPA-DUP", "subject": "x"})
        r = client.post("/api/erp/capas", json={"capa_no": "CAPA-DUP", "subject": "y"})
        assert r.status_code == 409

    def test_link_capa_to_complaint(self, client):
        cid, pid = self._setup(client)
        comp = client.post("/api/erp/complaints", json={
            "complaint_no": "CMP-LK", "customer_id": cid, "product_id": pid,
            "severity": "major",
        }).json()
        r = client.post("/api/erp/capas", json={
            "capa_no": "CAPA-LK",
            "capa_type": "corrective",
            "source_type": "complaint",
            "complaint_id": comp["id"],
            "subject": "客訴矯正",
            "severity": "major",
        })
        assert r.status_code == 201
        # 透過 complaint_id 篩選
        r = client.get(f"/api/erp/capas?complaint_id={comp['id']}")
        assert len(r.json()) == 1

    def test_filter_by_effectiveness(self, client):
        # 建立兩個 CAPA — 一個已驗證、一個未驗證
        client.post("/api/erp/capas", json={"capa_no": "CAPA-V1", "subject": "x"})
        c2 = client.post("/api/erp/capas", json={"capa_no": "CAPA-V2", "subject": "y"}).json()
        client.patch(f"/api/erp/capas/{c2['id']}", json={"effectiveness_verified": True})
        r = client.get("/api/erp/capas?effectiveness_verified=true")
        assert len(r.json()) == 1
        assert r.json()[0]["capa_no"] == "CAPA-V2"

    def test_preventive_capa_type(self, client):
        """預防措施 — 非由實際不符合觸發"""
        r = client.post("/api/erp/capas", json={
            "capa_no": "CAPA-PRE",
            "capa_type": "preventive",
            "source_type": "audit",
            "source_ref": "INT-AUDIT-2026-Q1",
            "subject": "預防性矯正：刀具更換頻率",
            "preventive_action": "建立每日刀具檢查表",
        })
        assert r.status_code == 201
        assert r.json()["capa_type"] == "preventive"
