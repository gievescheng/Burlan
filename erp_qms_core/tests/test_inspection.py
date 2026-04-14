"""Tests for Inspection Lot + Inspection Result (ISO 9001:2015 §8.6)."""
from __future__ import annotations

from erp_qms_core.domain.transitions import validate_status_transition
from erp_qms_core.repositories import inspection as insp_repo
from erp_qms_core.repositories import master as master_repo
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

class TestInspectionLotTransitions:
    def test_pending_to_in_progress(self):
        assert validate_status_transition("inspection_lot", "pending", "in_progress") is None

    def test_pending_to_passed_blocked(self):
        err = validate_status_transition("inspection_lot", "pending", "passed")
        assert err is not None

    def test_in_progress_to_passed(self):
        assert validate_status_transition("inspection_lot", "in_progress", "passed") is None

    def test_in_progress_to_failed(self):
        assert validate_status_transition("inspection_lot", "in_progress", "failed") is None

    def test_failed_can_reinspect(self):
        # 失敗後可重檢
        assert validate_status_transition("inspection_lot", "failed", "in_progress") is None

    def test_conditional_to_passed(self):
        # 待審可決議放行
        assert validate_status_transition("inspection_lot", "conditional", "passed") is None

    def test_passed_to_closed(self):
        assert validate_status_transition("inspection_lot", "passed", "closed") is None

    def test_closed_is_terminal(self):
        err = validate_status_transition("inspection_lot", "closed", "in_progress")
        assert err is not None


# ── Repository tests ───────────────────────────────────

class TestInspectionLotRepository:
    def test_create_and_get(self, db_session):
        wo, prod = _make_prereqs(db_session)
        lot = insp_repo.create_inspection_lot(db_session, {
            "lot_no": "INS-001",
            "work_order_id": wo.id,
            "product_id": prod.id,
            "inspection_type": "in_process",
            "sample_plan": "AQL 1.0 — MIL-STD-105E Level II",
            "total_qty": 100,
            "sample_size": 8,
            "source_lot_no": "LOT-A001",
            "inspector": "QC-01",
        })
        db_session.flush()
        assert lot.lot_no == "INS-001"
        assert lot.status == "pending"
        assert lot.inspection_type == "in_process"
        fetched = insp_repo.get_inspection_lot(db_session, lot.id)
        assert fetched is not None
        assert fetched.sample_plan.startswith("AQL")

    def test_create_with_results(self, db_session):
        wo, prod = _make_prereqs(db_session)
        lot = insp_repo.create_inspection_lot(db_session, {
            "lot_no": "INS-002", "work_order_id": wo.id, "product_id": prod.id,
            "sample_size": 8,
        }, results=[
            {"seq": 1, "item_name": "外觀", "actual_text": "OK"},
            {"seq": 2, "item_name": "厚度", "actual_value": 1.05,
             "lsl": 1.0, "usl": 1.1, "unit": "mm"},
            {"seq": 3, "item_name": "硬度", "actual_value": 95.0,
             "lsl": 90.0, "usl": 100.0, "unit": "HRC"},
        ])
        db_session.flush()
        assert len(lot.results) == 3
        # 全部 pass
        assert all(r.result == "pass" for r in lot.results)

    def test_filter_by_work_order(self, db_session):
        wo, prod = _make_prereqs(db_session)
        insp_repo.create_inspection_lot(db_session, {
            "lot_no": "INS-F01", "work_order_id": wo.id, "product_id": prod.id,
        })
        insp_repo.create_inspection_lot(db_session, {
            "lot_no": "INS-F02", "work_order_id": wo.id, "product_id": prod.id,
        })
        db_session.flush()
        results = insp_repo.list_inspection_lots(db_session, work_order_id=wo.id)
        assert len(results) == 2

    def test_filter_by_disposition(self, db_session):
        wo, prod = _make_prereqs(db_session)
        lot = insp_repo.create_inspection_lot(db_session, {
            "lot_no": "INS-D01", "work_order_id": wo.id, "product_id": prod.id,
        })
        db_session.flush()
        insp_repo.update_inspection_lot(db_session, lot.id, {
            "status": "passed", "disposition": "release",
        })
        db_session.flush()
        results = insp_repo.list_inspection_lots(db_session, disposition="release")
        assert len(results) == 1

    def test_update_replaces_results(self, db_session):
        wo, prod = _make_prereqs(db_session)
        lot = insp_repo.create_inspection_lot(db_session, {
            "lot_no": "INS-RPL", "work_order_id": wo.id, "product_id": prod.id,
        }, results=[
            {"seq": 1, "item_name": "old_item", "actual_text": "OK"},
        ])
        db_session.flush()
        updated = insp_repo.update_inspection_lot(db_session, lot.id, {}, results=[
            {"seq": 1, "item_name": "new_a", "actual_value": 5.0, "lsl": 1.0, "usl": 10.0},
            {"seq": 2, "item_name": "new_b", "actual_text": "OK"},
        ])
        assert len(updated.results) == 2
        names = [r.item_name for r in updated.results]
        assert "new_a" in names and "new_b" in names

    def test_delete_cascades_results(self, db_session):
        wo, prod = _make_prereqs(db_session)
        lot = insp_repo.create_inspection_lot(db_session, {
            "lot_no": "INS-DEL", "work_order_id": wo.id, "product_id": prod.id,
        }, results=[
            {"seq": 1, "item_name": "x", "actual_text": "OK"},
        ])
        db_session.flush()
        assert insp_repo.delete_inspection_lot(db_session, lot.id) is True
        assert insp_repo.get_inspection_lot(db_session, lot.id) is None


# ── Auto-judge tests ───────────────────────────────────

class TestAutoJudge:
    def test_text_ng_fails(self, db_session):
        wo, prod = _make_prereqs(db_session)
        lot = insp_repo.create_inspection_lot(db_session, {
            "lot_no": "INS-AJ01", "work_order_id": wo.id, "product_id": prod.id,
        }, results=[
            {"seq": 1, "item_name": "外觀", "actual_text": "NG", "defect_qty": 1},
        ])
        db_session.flush()
        assert lot.results[0].result == "fail"

    def test_value_below_lsl_fails(self, db_session):
        wo, prod = _make_prereqs(db_session)
        lot = insp_repo.create_inspection_lot(db_session, {
            "lot_no": "INS-AJ02", "work_order_id": wo.id, "product_id": prod.id,
        }, results=[
            {"seq": 1, "item_name": "厚度", "actual_value": 0.8,
             "lsl": 1.0, "usl": 1.1},
        ])
        db_session.flush()
        assert lot.results[0].result == "fail"

    def test_value_above_usl_fails(self, db_session):
        wo, prod = _make_prereqs(db_session)
        lot = insp_repo.create_inspection_lot(db_session, {
            "lot_no": "INS-AJ03", "work_order_id": wo.id, "product_id": prod.id,
        }, results=[
            {"seq": 1, "item_name": "硬度", "actual_value": 110,
             "lsl": 90, "usl": 100},
        ])
        db_session.flush()
        assert lot.results[0].result == "fail"

    def test_text_ok_passes(self, db_session):
        wo, prod = _make_prereqs(db_session)
        lot = insp_repo.create_inspection_lot(db_session, {
            "lot_no": "INS-AJ04", "work_order_id": wo.id, "product_id": prod.id,
        }, results=[
            {"seq": 1, "item_name": "外觀", "actual_text": "OK"},
        ])
        db_session.flush()
        assert lot.results[0].result == "pass"

    def test_reject_qty_auto_recompute(self, db_session):
        wo, prod = _make_prereqs(db_session)
        lot = insp_repo.create_inspection_lot(db_session, {
            "lot_no": "INS-AJ05", "work_order_id": wo.id, "product_id": prod.id,
            "sample_size": 10,
        }, results=[
            {"seq": 1, "item_name": "缺陷A", "actual_text": "NG", "defect_qty": 2},
            {"seq": 2, "item_name": "缺陷B", "actual_text": "NG", "defect_qty": 1},
        ])
        db_session.flush()
        assert lot.reject_qty == 3
        assert lot.accept_qty == 7  # 10 - 3


# ── API tests ──────────────────────────────────────────

class TestInspectionLotAPI:
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

    def test_create_inspection_lot(self, client):
        wo_id, pid = self._setup(client)
        resp = client.post("/api/erp/inspection-lots", json={
            "lot_no": "INS-001",
            "work_order_id": wo_id,
            "product_id": pid,
            "inspection_type": "final",
            "sample_plan": "AQL 1.0",
            "total_qty": 100,
            "sample_size": 8,
            "source_lot_no": "LOT-A001",
            "inspector": "QC-01",
        })
        assert resp.status_code == 201
        body = resp.json()
        assert body["lot_no"] == "INS-001"
        assert body["status"] == "pending"
        assert body["inspection_type"] == "final"

    def test_create_with_results_auto_judge(self, client):
        wo_id, pid = self._setup(client)
        resp = client.post("/api/erp/inspection-lots", json={
            "lot_no": "INS-002",
            "work_order_id": wo_id,
            "product_id": pid,
            "results": [
                {"seq": 1, "item_name": "外觀", "actual_text": "OK"},
                {"seq": 2, "item_name": "厚度", "actual_value": 0.8,
                 "lsl": 1.0, "usl": 1.1, "unit": "mm"},
            ],
        })
        assert resp.status_code == 201
        results = resp.json()["results"]
        assert results[0]["result"] == "pass"
        assert results[1]["result"] == "fail"

    def test_full_lifecycle_pass(self, client):
        wo_id, pid = self._setup(client)
        resp = client.post("/api/erp/inspection-lots", json={
            "lot_no": "INS-LP", "work_order_id": wo_id, "product_id": pid,
        })
        lot_id = resp.json()["id"]
        # pending → in_progress → passed → closed (with disposition)
        for target, disp in [
            ("in_progress", None),
            ("passed", None),
            ("closed", "release"),
        ]:
            payload = {"status": target}
            if disp:
                payload["disposition"] = disp
            r = client.patch(f"/api/erp/inspection-lots/{lot_id}", json=payload)
            assert r.status_code == 200, f"Failed at {target}: {r.json()}"
        final = client.get(f"/api/erp/inspection-lots/{lot_id}").json()
        assert final["status"] == "closed"
        assert final["disposition"] == "release"

    def test_failed_then_reinspect(self, client):
        wo_id, pid = self._setup(client)
        resp = client.post("/api/erp/inspection-lots", json={
            "lot_no": "INS-RE", "work_order_id": wo_id, "product_id": pid,
        })
        lot_id = resp.json()["id"]
        for target in ["in_progress", "failed", "in_progress", "passed", "closed"]:
            r = client.patch(f"/api/erp/inspection-lots/{lot_id}", json={"status": target})
            assert r.status_code == 200, f"Failed at {target}"

    def test_invalid_transition_422(self, client):
        wo_id, pid = self._setup(client)
        resp = client.post("/api/erp/inspection-lots", json={
            "lot_no": "INS-INV", "work_order_id": wo_id, "product_id": pid,
        })
        lot_id = resp.json()["id"]
        # pending → passed 不允許（必須先 in_progress）
        r = client.patch(f"/api/erp/inspection-lots/{lot_id}", json={"status": "passed"})
        assert r.status_code == 422

    def test_invalid_disposition_422(self, client):
        wo_id, pid = self._setup(client)
        resp = client.post("/api/erp/inspection-lots", json={
            "lot_no": "INS-D", "work_order_id": wo_id, "product_id": pid,
        })
        lot_id = resp.json()["id"]
        r = client.patch(f"/api/erp/inspection-lots/{lot_id}",
                         json={"disposition": "scrap_unauthorized"})
        assert r.status_code == 422

    def test_invalid_inspection_type_422(self, client):
        wo_id, pid = self._setup(client)
        r = client.post("/api/erp/inspection-lots", json={
            "lot_no": "INS-IT", "work_order_id": wo_id, "product_id": pid,
            "inspection_type": "weird_type",
        })
        assert r.status_code == 422

    def test_duplicate_lot_no_409(self, client):
        wo_id, pid = self._setup(client)
        client.post("/api/erp/inspection-lots", json={
            "lot_no": "INS-DUP", "work_order_id": wo_id, "product_id": pid,
        })
        r = client.post("/api/erp/inspection-lots", json={
            "lot_no": "INS-DUP", "work_order_id": wo_id, "product_id": pid,
        })
        assert r.status_code == 409

    def test_filter_by_inspection_type(self, client):
        wo_id, pid = self._setup(client)
        client.post("/api/erp/inspection-lots", json={
            "lot_no": "INS-T1", "work_order_id": wo_id, "product_id": pid,
            "inspection_type": "incoming",
        })
        client.post("/api/erp/inspection-lots", json={
            "lot_no": "INS-T2", "work_order_id": wo_id, "product_id": pid,
            "inspection_type": "final",
        })
        r = client.get("/api/erp/inspection-lots?inspection_type=incoming")
        assert r.status_code == 200
        assert len(r.json()) == 1
        assert r.json()[0]["lot_no"] == "INS-T1"

    def test_traceability_to_source_lot(self, client):
        wo_id, pid = self._setup(client)
        client.post("/api/erp/inspection-lots", json={
            "lot_no": "INS-S1", "work_order_id": wo_id, "product_id": pid,
            "source_lot_no": "LOT-X",
        })
        client.post("/api/erp/inspection-lots", json={
            "lot_no": "INS-S2", "work_order_id": wo_id, "product_id": pid,
            "source_lot_no": "LOT-Y",
        })
        r = client.get("/api/erp/inspection-lots?source_lot_no=LOT-X")
        assert len(r.json()) == 1

    def test_delete_inspection_lot(self, client):
        wo_id, pid = self._setup(client)
        resp = client.post("/api/erp/inspection-lots", json={
            "lot_no": "INS-DEL", "work_order_id": wo_id, "product_id": pid,
        })
        lot_id = resp.json()["id"]
        r = client.delete(f"/api/erp/inspection-lots/{lot_id}")
        assert r.status_code == 204
        r = client.get(f"/api/erp/inspection-lots/{lot_id}")
        assert r.status_code == 404
