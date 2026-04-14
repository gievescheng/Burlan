"""Tests for Production Log and Process Param Check."""
from __future__ import annotations

from erp_qms_core.repositories import logging as log_repo
from erp_qms_core.repositories import master as master_repo
from erp_qms_core.repositories import order as order_repo


# ── helpers ────────────────────────────────────────────

def _make_prereqs(session):
    """Create customer, product, sales order, work order for FK references."""
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


# ── Repository tests ──────────────────────────────────

class TestProductionLogRepository:
    def test_create_and_get(self, db_session):
        wo, prod = _make_prereqs(db_session)
        log = log_repo.create_production_log(db_session, {
            "log_no": "PL-001",
            "work_order_id": wo.id,
            "product_id": prod.id,
            "input_qty": 100,
            "output_qty": 95,
            "defect_qty": 3,
            "scrap_qty": 2,
            "lot_no": "LOT-A001",
            "shift": "day",
            "operator": "OP-01",
        })
        db_session.flush()
        assert log.log_no == "PL-001"
        assert log.input_qty == 100
        assert log.status == "recorded"
        fetched = log_repo.get_production_log(db_session, log.id)
        assert fetched is not None
        assert fetched.lot_no == "LOT-A001"

    def test_create_with_param_checks(self, db_session):
        wo, prod = _make_prereqs(db_session)
        log = log_repo.create_production_log(db_session, {
            "log_no": "PL-002",
            "work_order_id": wo.id,
            "product_id": prod.id,
        }, param_checks=[
            {"seq": 1, "param_name": "temperature", "param_value": 25.0,
             "lsl": 20.0, "usl": 30.0, "target": 25.0, "unit": "C"},
            {"seq": 2, "param_name": "pressure", "param_value": 1.5,
             "lsl": 1.0, "usl": 2.0, "unit": "atm"},
        ])
        db_session.flush()
        assert len(log.param_checks) == 2
        assert log.param_checks[0].param_name == "temperature"
        assert log.param_checks[1].param_name == "pressure"

    def test_duplicate_log_no_blocked(self, db_session):
        wo, prod = _make_prereqs(db_session)
        log_repo.create_production_log(db_session, {
            "log_no": "PL-DUP", "work_order_id": wo.id, "product_id": prod.id,
        })
        db_session.flush()
        dup = log_repo.get_production_log_by_no(db_session, "PL-DUP")
        assert dup is not None

    def test_filter_by_work_order(self, db_session):
        wo, prod = _make_prereqs(db_session)
        log_repo.create_production_log(db_session, {
            "log_no": "PL-F01", "work_order_id": wo.id, "product_id": prod.id,
        })
        log_repo.create_production_log(db_session, {
            "log_no": "PL-F02", "work_order_id": wo.id, "product_id": prod.id,
        })
        db_session.flush()
        results = log_repo.list_production_logs(db_session, work_order_id=wo.id)
        assert len(results) == 2

    def test_filter_by_lot_no(self, db_session):
        wo, prod = _make_prereqs(db_session)
        log_repo.create_production_log(db_session, {
            "log_no": "PL-L01", "work_order_id": wo.id, "product_id": prod.id,
            "lot_no": "LOT-X",
        })
        log_repo.create_production_log(db_session, {
            "log_no": "PL-L02", "work_order_id": wo.id, "product_id": prod.id,
            "lot_no": "LOT-Y",
        })
        db_session.flush()
        results = log_repo.list_production_logs(db_session, lot_no="LOT-X")
        assert len(results) == 1
        assert results[0].lot_no == "LOT-X"

    def test_update_production_log(self, db_session):
        wo, prod = _make_prereqs(db_session)
        log = log_repo.create_production_log(db_session, {
            "log_no": "PL-UPD", "work_order_id": wo.id, "product_id": prod.id,
            "output_qty": 50,
        })
        db_session.flush()
        updated = log_repo.update_production_log(db_session, log.id, {"output_qty": 80})
        assert updated.output_qty == 80

    def test_update_replaces_param_checks(self, db_session):
        wo, prod = _make_prereqs(db_session)
        log = log_repo.create_production_log(db_session, {
            "log_no": "PL-RPC", "work_order_id": wo.id, "product_id": prod.id,
        }, param_checks=[
            {"seq": 1, "param_name": "old_param", "param_value": 1.0},
        ])
        db_session.flush()
        assert len(log.param_checks) == 1

        updated = log_repo.update_production_log(db_session, log.id, {}, param_checks=[
            {"seq": 1, "param_name": "new_param_a", "param_value": 2.0},
            {"seq": 2, "param_name": "new_param_b", "param_value": 3.0},
        ])
        assert len(updated.param_checks) == 2
        names = [pc.param_name for pc in updated.param_checks]
        assert "new_param_a" in names
        assert "new_param_b" in names

    def test_delete_cascades_checks(self, db_session):
        wo, prod = _make_prereqs(db_session)
        log = log_repo.create_production_log(db_session, {
            "log_no": "PL-DEL", "work_order_id": wo.id, "product_id": prod.id,
        }, param_checks=[
            {"seq": 1, "param_name": "temp", "param_value": 25.0},
        ])
        db_session.flush()
        assert log_repo.delete_production_log(db_session, log.id) is True
        assert log_repo.get_production_log(db_session, log.id) is None


# ── Auto-judge tests ──────────────────────────────────

class TestAutoJudge:
    def test_pass_within_limits(self, db_session):
        wo, prod = _make_prereqs(db_session)
        log = log_repo.create_production_log(db_session, {
            "log_no": "PL-AJ01", "work_order_id": wo.id, "product_id": prod.id,
        }, param_checks=[
            {"seq": 1, "param_name": "temp", "param_value": 25.0,
             "lsl": 20.0, "usl": 30.0},
        ])
        db_session.flush()
        assert log.param_checks[0].result == "pass"

    def test_fail_below_lsl(self, db_session):
        wo, prod = _make_prereqs(db_session)
        log = log_repo.create_production_log(db_session, {
            "log_no": "PL-AJ02", "work_order_id": wo.id, "product_id": prod.id,
        }, param_checks=[
            {"seq": 1, "param_name": "temp", "param_value": 15.0,
             "lsl": 20.0, "usl": 30.0},
        ])
        db_session.flush()
        assert log.param_checks[0].result == "fail"

    def test_fail_above_usl(self, db_session):
        wo, prod = _make_prereqs(db_session)
        log = log_repo.create_production_log(db_session, {
            "log_no": "PL-AJ03", "work_order_id": wo.id, "product_id": prod.id,
        }, param_checks=[
            {"seq": 1, "param_name": "temp", "param_value": 35.0,
             "lsl": 20.0, "usl": 30.0},
        ])
        db_session.flush()
        assert log.param_checks[0].result == "fail"

    def test_explicit_fail_preserved(self, db_session):
        wo, prod = _make_prereqs(db_session)
        log = log_repo.create_production_log(db_session, {
            "log_no": "PL-AJ04", "work_order_id": wo.id, "product_id": prod.id,
        }, param_checks=[
            {"seq": 1, "param_name": "visual", "param_value": 0.0,
             "result": "fail"},
        ])
        db_session.flush()
        assert log.param_checks[0].result == "fail"

    def test_no_limits_passes(self, db_session):
        wo, prod = _make_prereqs(db_session)
        log = log_repo.create_production_log(db_session, {
            "log_no": "PL-AJ05", "work_order_id": wo.id, "product_id": prod.id,
        }, param_checks=[
            {"seq": 1, "param_name": "note_value", "param_value": 999.0},
        ])
        db_session.flush()
        assert log.param_checks[0].result == "pass"


# ── API tests ─────────────────────────────────────────

class TestProductionLogAPI:
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

    def test_create_production_log(self, client):
        wo_id, pid = self._setup(client)
        resp = client.post("/api/erp/production-logs", json={
            "log_no": "PL-001",
            "work_order_id": wo_id,
            "product_id": pid,
            "input_qty": 100,
            "output_qty": 95,
            "lot_no": "LOT-A001",
            "operator": "OP-01",
            "shift": "day",
        })
        assert resp.status_code == 201
        body = resp.json()
        assert body["log_no"] == "PL-001"
        assert body["status"] == "recorded"
        assert body["input_qty"] == 100
        assert body["lot_no"] == "LOT-A001"

    def test_create_with_param_checks_and_auto_judge(self, client):
        wo_id, pid = self._setup(client)
        resp = client.post("/api/erp/production-logs", json={
            "log_no": "PL-002",
            "work_order_id": wo_id,
            "product_id": pid,
            "param_checks": [
                {"seq": 1, "param_name": "temperature", "param_value": 25.0,
                 "lsl": 20.0, "usl": 30.0, "unit": "C"},
                {"seq": 2, "param_name": "pressure", "param_value": 0.5,
                 "lsl": 1.0, "usl": 2.0, "unit": "atm"},
            ],
        })
        assert resp.status_code == 201
        checks = resp.json()["param_checks"]
        assert len(checks) == 2
        assert checks[0]["result"] == "pass"
        assert checks[1]["result"] == "fail"  # 0.5 < lsl=1.0

    def test_duplicate_log_no_409(self, client):
        wo_id, pid = self._setup(client)
        client.post("/api/erp/production-logs", json={
            "log_no": "PL-DUP", "work_order_id": wo_id, "product_id": pid,
        })
        resp = client.post("/api/erp/production-logs", json={
            "log_no": "PL-DUP", "work_order_id": wo_id, "product_id": pid,
        })
        assert resp.status_code == 409

    def test_list_filter_by_work_order(self, client):
        wo_id, pid = self._setup(client)
        client.post("/api/erp/production-logs", json={
            "log_no": "PL-A", "work_order_id": wo_id, "product_id": pid,
        })
        client.post("/api/erp/production-logs", json={
            "log_no": "PL-B", "work_order_id": wo_id, "product_id": pid,
        })
        resp = client.get(f"/api/erp/production-logs?work_order_id={wo_id}")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_update_status_and_quantities(self, client):
        wo_id, pid = self._setup(client)
        resp = client.post("/api/erp/production-logs", json={
            "log_no": "PL-UPD", "work_order_id": wo_id, "product_id": pid,
        })
        log_id = resp.json()["id"]
        resp = client.patch(f"/api/erp/production-logs/{log_id}", json={
            "status": "verified", "output_qty": 90,
        })
        assert resp.status_code == 200
        assert resp.json()["status"] == "verified"
        assert resp.json()["output_qty"] == 90

    def test_invalid_status_422(self, client):
        wo_id, pid = self._setup(client)
        resp = client.post("/api/erp/production-logs", json={
            "log_no": "PL-INV", "work_order_id": wo_id, "product_id": pid,
        })
        log_id = resp.json()["id"]
        resp = client.patch(f"/api/erp/production-logs/{log_id}", json={
            "status": "nonexistent",
        })
        assert resp.status_code == 422

    def test_delete_production_log(self, client):
        wo_id, pid = self._setup(client)
        resp = client.post("/api/erp/production-logs", json={
            "log_no": "PL-DEL", "work_order_id": wo_id, "product_id": pid,
        })
        log_id = resp.json()["id"]
        resp = client.delete(f"/api/erp/production-logs/{log_id}")
        assert resp.status_code == 204
        resp = client.get(f"/api/erp/production-logs/{log_id}")
        assert resp.status_code == 404

    def test_get_not_found(self, client):
        resp = client.get("/api/erp/production-logs/nonexistent")
        assert resp.status_code == 404
