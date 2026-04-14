"""Tests for NCR + Rework Order (ISO 9001:2015 §8.7 不合格品輸出管制)."""
from __future__ import annotations

from erp_qms_core.domain.transitions import validate_status_transition
from erp_qms_core.repositories import master as master_repo
from erp_qms_core.repositories import nonconformance as ncr_repo
from erp_qms_core.repositories import order as order_repo


# ── helpers ────────────────────────────────────────────

def _make_prereqs(session):
    cust = master_repo.create_customer(session, {"customer_code": "C001", "name": "Acme"})
    prod = master_repo.create_product(session, {"product_code": "P001", "name": "Widget"})
    session.flush()
    so = order_repo.create_sales_order(session, {"order_no": "SO-001", "customer_id": cust.id})
    session.flush()
    wo = order_repo.create_work_order(session, {
        "wo_no": "WO-001", "product_id": prod.id,
        "sales_order_id": so.id, "planned_qty": 100,
    })
    session.flush()
    return wo, prod


# ── Domain transitions ─────────────────────────────────

class TestNCRTransitions:
    def test_open_to_under_review(self):
        assert validate_status_transition("ncr", "open", "under_review") is None

    def test_open_directly_to_disposition_decided(self):
        # 簡單案例：發現後直接判定處置
        assert validate_status_transition("ncr", "open", "disposition_decided") is None

    def test_open_to_closed_blocked(self):
        # 不可跳過處置直接關閉
        err = validate_status_transition("ncr", "open", "closed")
        assert err is not None

    def test_disposition_decided_to_in_action(self):
        assert validate_status_transition(
            "ncr", "disposition_decided", "in_action",
        ) is None

    def test_in_action_to_closed(self):
        assert validate_status_transition("ncr", "in_action", "closed") is None

    def test_closed_is_terminal(self):
        err = validate_status_transition("ncr", "closed", "open")
        assert err is not None

    def test_cancellable_at_any_open_state(self):
        for src in ("open", "under_review", "disposition_decided", "in_action"):
            assert validate_status_transition("ncr", src, "cancelled") is None


class TestReworkTransitions:
    def test_planned_to_in_progress(self):
        assert validate_status_transition("rework_order", "planned", "in_progress") is None

    def test_planned_to_completed_blocked(self):
        err = validate_status_transition("rework_order", "planned", "completed")
        assert err is not None

    def test_in_progress_to_completed(self):
        assert validate_status_transition(
            "rework_order", "in_progress", "completed",
        ) is None

    def test_completed_is_terminal(self):
        err = validate_status_transition("rework_order", "completed", "in_progress")
        assert err is not None


# ── NCR Repository ─────────────────────────────────────

class TestNCRRepository:
    def test_create_and_get(self, db_session):
        wo, prod = _make_prereqs(db_session)
        ncr = ncr_repo.create_ncr(db_session, {
            "ncr_no": "NCR-001",
            "work_order_id": wo.id,
            "product_id": prod.id,
            "defect_qty": 5,
            "total_qty": 100,
            "defect_code": "D-SCR-01",
            "defect_description": "表面刮傷",
            "severity": "major",
            "category": "process",
            "lot_no": "LOT-A001",
            "reported_by": "QC-01",
        })
        db_session.flush()
        assert ncr.ncr_no == "NCR-001"
        assert ncr.status == "open"
        assert ncr.severity == "major"
        fetched = ncr_repo.get_ncr(db_session, ncr.id)
        assert fetched is not None
        assert fetched.defect_description == "表面刮傷"

    def test_filter_by_severity(self, db_session):
        wo, prod = _make_prereqs(db_session)
        ncr_repo.create_ncr(db_session, {
            "ncr_no": "NCR-S1", "work_order_id": wo.id, "product_id": prod.id,
            "severity": "critical",
        })
        ncr_repo.create_ncr(db_session, {
            "ncr_no": "NCR-S2", "work_order_id": wo.id, "product_id": prod.id,
            "severity": "minor",
        })
        db_session.flush()
        results = ncr_repo.list_ncrs(db_session, severity="critical")
        assert len(results) == 1
        assert results[0].ncr_no == "NCR-S1"

    def test_filter_by_requires_capa(self, db_session):
        wo, prod = _make_prereqs(db_session)
        ncr_repo.create_ncr(db_session, {
            "ncr_no": "NCR-C1", "work_order_id": wo.id, "product_id": prod.id,
            "requires_capa": True,
        })
        ncr_repo.create_ncr(db_session, {
            "ncr_no": "NCR-C2", "work_order_id": wo.id, "product_id": prod.id,
            "requires_capa": False,
        })
        db_session.flush()
        results = ncr_repo.list_ncrs(db_session, requires_capa=True)
        assert len(results) == 1

    def test_traceability_to_inspection_lot(self, db_session):
        wo, prod = _make_prereqs(db_session)
        # 模擬：來自檢驗失敗
        from erp_qms_core.repositories import inspection as insp_repo
        lot = insp_repo.create_inspection_lot(db_session, {
            "lot_no": "INS-T1", "work_order_id": wo.id, "product_id": prod.id,
        })
        db_session.flush()
        ncr = ncr_repo.create_ncr(db_session, {
            "ncr_no": "NCR-T1", "work_order_id": wo.id, "product_id": prod.id,
            "inspection_lot_id": lot.id,
        })
        db_session.flush()
        results = ncr_repo.list_ncrs(db_session, inspection_lot_id=lot.id)
        assert len(results) == 1
        assert results[0].id == ncr.id

    def test_delete_cascades_rework(self, db_session):
        wo, prod = _make_prereqs(db_session)
        ncr = ncr_repo.create_ncr(db_session, {
            "ncr_no": "NCR-DEL", "work_order_id": wo.id, "product_id": prod.id,
            "disposition": "rework",
        })
        db_session.flush()
        ncr_repo.create_rework_order(db_session, ncr.id, {
            "rework_no": "RW-DEL-1", "work_order_id": wo.id, "product_id": prod.id,
            "rework_qty": 5,
        })
        db_session.flush()
        assert ncr_repo.delete_ncr(db_session, ncr.id) is True
        assert ncr_repo.get_ncr(db_session, ncr.id) is None
        # 重工單也應被級聯刪除
        rws = ncr_repo.list_rework_orders(db_session, ncr_id=ncr.id)
        assert len(rws) == 0


# ── Rework Repository ──────────────────────────────────

class TestReworkRepository:
    def test_create_and_filter(self, db_session):
        wo, prod = _make_prereqs(db_session)
        ncr = ncr_repo.create_ncr(db_session, {
            "ncr_no": "NCR-RW", "work_order_id": wo.id, "product_id": prod.id,
            "disposition": "rework",
        })
        db_session.flush()
        rw = ncr_repo.create_rework_order(db_session, ncr.id, {
            "rework_no": "RW-001",
            "work_order_id": wo.id,
            "product_id": prod.id,
            "rework_qty": 10,
            "method": "重新研磨",
            "assigned_to": "OP-RW-01",
        })
        db_session.flush()
        assert rw.rework_no == "RW-001"
        assert rw.status == "planned"
        rws = ncr_repo.list_rework_orders(db_session, ncr_id=ncr.id)
        assert len(rws) == 1


# ── NCR API ────────────────────────────────────────────

class TestNCRAPI:
    def _setup(self, client):
        c = client.post("/api/erp/customers", json={"customer_code": "C001", "name": "Acme"})
        p = client.post("/api/erp/products", json={"product_code": "P001", "name": "Widget"})
        pid = p.json()["id"]
        so = client.post("/api/erp/sales-orders", json={
            "order_no": "SO-001", "customer_id": c.json()["id"],
        })
        wo = client.post("/api/erp/work-orders", json={
            "wo_no": "WO-001", "product_id": pid, "planned_qty": 100,
            "sales_order_id": so.json()["id"],
        })
        return wo.json()["id"], pid

    def test_create_ncr(self, client):
        wo_id, pid = self._setup(client)
        resp = client.post("/api/erp/ncrs", json={
            "ncr_no": "NCR-001",
            "work_order_id": wo_id,
            "product_id": pid,
            "defect_qty": 3,
            "total_qty": 100,
            "defect_code": "D-DIM-01",
            "defect_description": "尺寸超出公差",
            "severity": "major",
            "category": "process",
            "lot_no": "LOT-A001",
            "reported_by": "QC-01",
        })
        assert resp.status_code == 201
        body = resp.json()
        assert body["ncr_no"] == "NCR-001"
        assert body["status"] == "open"
        assert body["severity"] == "major"
        assert body["requires_capa"] is False  # major 不強制 CAPA

    def test_critical_auto_requires_capa(self, client):
        """ISO 10.2 — 重大不符合須觸發矯正措施"""
        wo_id, pid = self._setup(client)
        resp = client.post("/api/erp/ncrs", json={
            "ncr_no": "NCR-CRIT",
            "work_order_id": wo_id, "product_id": pid,
            "severity": "critical",
        })
        assert resp.status_code == 201
        assert resp.json()["requires_capa"] is True

    def test_full_lifecycle(self, client):
        wo_id, pid = self._setup(client)
        resp = client.post("/api/erp/ncrs", json={
            "ncr_no": "NCR-LP", "work_order_id": wo_id, "product_id": pid,
        })
        ncr_id = resp.json()["id"]
        # open → under_review → disposition_decided → in_action → closed
        for target in ["under_review", "disposition_decided", "in_action", "closed"]:
            r = client.patch(f"/api/erp/ncrs/{ncr_id}", json={"status": target})
            assert r.status_code == 200, f"Failed at {target}: {r.json()}"

    def test_setting_disposition_advances_status(self, client):
        """設定處置時，狀態自動推進到 disposition_decided"""
        wo_id, pid = self._setup(client)
        resp = client.post("/api/erp/ncrs", json={
            "ncr_no": "NCR-DA", "work_order_id": wo_id, "product_id": pid,
        })
        ncr_id = resp.json()["id"]
        r = client.patch(f"/api/erp/ncrs/{ncr_id}", json={
            "disposition": "scrap", "disposition_by": "QM-01",
        })
        assert r.status_code == 200
        assert r.json()["status"] == "disposition_decided"
        assert r.json()["disposition"] == "scrap"

    def test_invalid_disposition_422(self, client):
        wo_id, pid = self._setup(client)
        resp = client.post("/api/erp/ncrs", json={
            "ncr_no": "NCR-IDP", "work_order_id": wo_id, "product_id": pid,
        })
        ncr_id = resp.json()["id"]
        r = client.patch(f"/api/erp/ncrs/{ncr_id}", json={
            "disposition": "throw_away_secretly",
        })
        assert r.status_code == 422

    def test_invalid_severity_422(self, client):
        wo_id, pid = self._setup(client)
        r = client.post("/api/erp/ncrs", json={
            "ncr_no": "NCR-IS", "work_order_id": wo_id, "product_id": pid,
            "severity": "catastrophic",
        })
        assert r.status_code == 422

    def test_invalid_category_422(self, client):
        wo_id, pid = self._setup(client)
        r = client.post("/api/erp/ncrs", json={
            "ncr_no": "NCR-IC", "work_order_id": wo_id, "product_id": pid,
            "category": "alien_invasion",
        })
        assert r.status_code == 422

    def test_skip_disposition_blocked_422(self, client):
        wo_id, pid = self._setup(client)
        resp = client.post("/api/erp/ncrs", json={
            "ncr_no": "NCR-SKP", "work_order_id": wo_id, "product_id": pid,
        })
        ncr_id = resp.json()["id"]
        # open → closed 不允許
        r = client.patch(f"/api/erp/ncrs/{ncr_id}", json={"status": "closed"})
        assert r.status_code == 422

    def test_duplicate_ncr_no_409(self, client):
        wo_id, pid = self._setup(client)
        client.post("/api/erp/ncrs", json={
            "ncr_no": "NCR-DUP", "work_order_id": wo_id, "product_id": pid,
        })
        r = client.post("/api/erp/ncrs", json={
            "ncr_no": "NCR-DUP", "work_order_id": wo_id, "product_id": pid,
        })
        assert r.status_code == 409

    def test_filter_capa_required(self, client):
        wo_id, pid = self._setup(client)
        client.post("/api/erp/ncrs", json={
            "ncr_no": "NCR-FC1", "work_order_id": wo_id, "product_id": pid,
            "severity": "critical",  # 自動 requires_capa=True
        })
        client.post("/api/erp/ncrs", json={
            "ncr_no": "NCR-FC2", "work_order_id": wo_id, "product_id": pid,
            "severity": "minor",
        })
        r = client.get("/api/erp/ncrs?requires_capa=true")
        assert r.status_code == 200
        assert len(r.json()) == 1
        assert r.json()[0]["ncr_no"] == "NCR-FC1"


# ── Rework API ─────────────────────────────────────────

class TestReworkAPI:
    def _setup_with_ncr(self, client, disposition="rework"):
        c = client.post("/api/erp/customers", json={"customer_code": "C001", "name": "Acme"})
        p = client.post("/api/erp/products", json={"product_code": "P001", "name": "Widget"})
        pid = p.json()["id"]
        so = client.post("/api/erp/sales-orders", json={
            "order_no": "SO-001", "customer_id": c.json()["id"],
        })
        wo_id = client.post("/api/erp/work-orders", json={
            "wo_no": "WO-001", "product_id": pid, "planned_qty": 100,
            "sales_order_id": so.json()["id"],
        }).json()["id"]
        ncr = client.post("/api/erp/ncrs", json={
            "ncr_no": "NCR-RW01", "work_order_id": wo_id, "product_id": pid,
            "defect_qty": 5,
        }).json()
        if disposition:
            client.patch(f"/api/erp/ncrs/{ncr['id']}", json={"disposition": disposition})
        return ncr["id"], wo_id, pid

    def test_create_rework_for_rework_disposition(self, client):
        ncr_id, wo_id, pid = self._setup_with_ncr(client, disposition="rework")
        r = client.post(f"/api/erp/ncrs/{ncr_id}/rework-orders", json={
            "rework_no": "RW-001",
            "work_order_id": wo_id,
            "product_id": pid,
            "rework_qty": 5,
            "method": "重新研磨",
            "assigned_to": "OP-RW-01",
        })
        assert r.status_code == 201
        assert r.json()["status"] == "planned"
        assert r.json()["rework_no"] == "RW-001"

    def test_create_rework_blocked_when_disposition_not_rework(self, client):
        ncr_id, wo_id, pid = self._setup_with_ncr(client, disposition="scrap")
        r = client.post(f"/api/erp/ncrs/{ncr_id}/rework-orders", json={
            "rework_no": "RW-NOPE", "work_order_id": wo_id, "product_id": pid,
            "rework_qty": 5,
        })
        assert r.status_code == 422

    def test_rework_lifecycle_passed(self, client):
        ncr_id, wo_id, pid = self._setup_with_ncr(client)
        rw = client.post(f"/api/erp/ncrs/{ncr_id}/rework-orders", json={
            "rework_no": "RW-LP", "work_order_id": wo_id, "product_id": pid,
            "rework_qty": 5,
        }).json()
        # planned → in_progress → completed (passed)
        for target in ["in_progress", "completed"]:
            r = client.patch(f"/api/erp/rework-orders/{rw['id']}", json={"status": target})
            assert r.status_code == 200
        r = client.patch(f"/api/erp/rework-orders/{rw['id']}", json={
            "result": "passed", "success_qty": 5,
        })
        assert r.status_code == 200
        assert r.json()["result"] == "passed"
        assert r.json()["success_qty"] == 5

    def test_rework_invalid_status_422(self, client):
        ncr_id, wo_id, pid = self._setup_with_ncr(client)
        rw = client.post(f"/api/erp/ncrs/{ncr_id}/rework-orders", json={
            "rework_no": "RW-IS", "work_order_id": wo_id, "product_id": pid,
            "rework_qty": 1,
        }).json()
        # planned → completed 不允許（須先 in_progress）
        r = client.patch(f"/api/erp/rework-orders/{rw['id']}", json={"status": "completed"})
        assert r.status_code == 422

    def test_rework_invalid_result_422(self, client):
        ncr_id, wo_id, pid = self._setup_with_ncr(client)
        rw = client.post(f"/api/erp/ncrs/{ncr_id}/rework-orders", json={
            "rework_no": "RW-IR", "work_order_id": wo_id, "product_id": pid,
            "rework_qty": 1,
        }).json()
        r = client.patch(f"/api/erp/rework-orders/{rw['id']}", json={"result": "maybe"})
        assert r.status_code == 422

    def test_filter_rework_by_ncr(self, client):
        ncr_id, wo_id, pid = self._setup_with_ncr(client)
        client.post(f"/api/erp/ncrs/{ncr_id}/rework-orders", json={
            "rework_no": "RW-F1", "work_order_id": wo_id, "product_id": pid,
            "rework_qty": 1,
        })
        r = client.get(f"/api/erp/rework-orders?ncr_id={ncr_id}")
        assert r.status_code == 200
        assert len(r.json()) == 1

    def test_create_rework_for_missing_ncr_404(self, client):
        ncr_id, wo_id, pid = self._setup_with_ncr(client)
        r = client.post("/api/erp/ncrs/nonexistent/rework-orders", json={
            "rework_no": "RW-X", "work_order_id": wo_id, "product_id": pid,
            "rework_qty": 1,
        })
        assert r.status_code == 404
