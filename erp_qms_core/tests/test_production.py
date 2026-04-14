"""Tests for Production Plan and Material Issue."""
from __future__ import annotations

from erp_qms_core.domain.transitions import validate_status_transition
from erp_qms_core.repositories import master as master_repo
from erp_qms_core.repositories import order as order_repo
from erp_qms_core.repositories import production as prod_repo


# ── Domain transitions ─────────────────────────────────

class TestProductionPlanTransitions:
    def test_draft_to_approved(self):
        assert validate_status_transition("production_plan", "draft", "approved") is None

    def test_skip_approved_blocked(self):
        err = validate_status_transition("production_plan", "draft", "in_progress")
        assert err is not None

    def test_completed_to_closed(self):
        assert validate_status_transition("production_plan", "completed", "closed") is None


class TestMaterialIssueTransitions:
    def test_draft_to_approved(self):
        assert validate_status_transition("material_issue", "draft", "approved") is None

    def test_approved_to_issued(self):
        assert validate_status_transition("material_issue", "approved", "issued") is None

    def test_issued_to_completed(self):
        assert validate_status_transition("material_issue", "issued", "completed") is None

    def test_completed_is_terminal(self):
        err = validate_status_transition("material_issue", "completed", "draft")
        assert err is not None


# ── Repository tests ────────────────────────────────────

def _make_wo(session):
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


class TestProductionPlanRepository:
    def test_create_and_get(self, db_session):
        wo, prod = _make_wo(db_session)
        pp = prod_repo.create_production_plan(db_session, {
            "plan_no": "PP-001",
            "work_order_id": wo.id,
            "product_id": prod.id,
            "planned_qty": 100,
            "shift": "day",
        })
        db_session.flush()
        assert pp.plan_no == "PP-001"
        assert pp.shift == "day"
        assert prod_repo.get_production_plan(db_session, pp.id) is not None

    def test_filter_by_wo(self, db_session):
        wo, prod = _make_wo(db_session)
        prod_repo.create_production_plan(db_session, {
            "plan_no": "PP-001", "work_order_id": wo.id,
            "product_id": prod.id, "planned_qty": 50,
        })
        db_session.flush()

        results = prod_repo.list_production_plans(db_session, work_order_id=wo.id)
        assert len(results) == 1


class TestMaterialIssueRepository:
    def test_create_with_items(self, db_session):
        wo, prod = _make_wo(db_session)
        mi = prod_repo.create_material_issue(db_session, {
            "issue_no": "MI-001",
            "work_order_id": wo.id,
            "issued_by": "operator_A",
        }, items=[
            {"product_id": prod.id, "seq": 1, "requested_qty": 50, "lot_no": "MAT-LOT-001"},
        ])
        db_session.flush()
        assert mi.issue_no == "MI-001"
        assert len(mi.items) == 1
        assert mi.items[0].lot_no == "MAT-LOT-001"

    def test_delete_cascades_items(self, db_session):
        wo, prod = _make_wo(db_session)
        mi = prod_repo.create_material_issue(db_session, {
            "issue_no": "MI-001", "work_order_id": wo.id,
        }, items=[
            {"product_id": prod.id, "seq": 1, "requested_qty": 10},
        ])
        db_session.flush()
        assert prod_repo.delete_material_issue(db_session, mi.id) is True
        assert prod_repo.get_material_issue(db_session, mi.id) is None


# ── API tests ───────────────────────────────────────────

class TestProductionPlanAPI:
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

    def test_full_lifecycle(self, client):
        wo_id, pid = self._setup(client)

        resp = client.post("/api/erp/production-plans", json={
            "plan_no": "PP-001",
            "work_order_id": wo_id,
            "product_id": pid,
            "planned_qty": 100,
            "shift": "day",
        })
        assert resp.status_code == 201
        pp = resp.json()
        assert pp["status"] == "draft"

        # draft → approved → in_progress → completed → closed
        for target in ["approved", "in_progress", "completed", "closed"]:
            resp = client.patch(f"/api/erp/production-plans/{pp['id']}", json={"status": target})
            assert resp.status_code == 200, f"Failed: {target}"

    def test_illegal_transition(self, client):
        wo_id, pid = self._setup(client)
        resp = client.post("/api/erp/production-plans", json={
            "plan_no": "PP-001", "work_order_id": wo_id,
            "product_id": pid, "planned_qty": 50,
        })
        pp_id = resp.json()["id"]
        resp = client.patch(f"/api/erp/production-plans/{pp_id}", json={"status": "completed"})
        assert resp.status_code == 422


class TestMaterialIssueAPI:
    def _setup(self, client):
        c = client.post("/api/erp/customers", json={"customer_code": "C001", "name": "Acme"})
        p = client.post("/api/erp/products", json={"product_code": "P001", "name": "Widget"})
        pid = p.json()["id"]
        wo = client.post("/api/erp/work-orders", json={
            "wo_no": "WO-001", "product_id": pid, "planned_qty": 100,
        })
        return wo.json()["id"], pid

    def test_create_with_items_and_transitions(self, client):
        wo_id, pid = self._setup(client)

        resp = client.post("/api/erp/material-issues", json={
            "issue_no": "MI-001",
            "work_order_id": wo_id,
            "issued_by": "operator_A",
            "items": [
                {"product_id": pid, "seq": 1, "requested_qty": 50, "lot_no": "MAT-001"},
            ],
        })
        assert resp.status_code == 201
        mi = resp.json()
        assert len(mi["items"]) == 1
        assert mi["items"][0]["lot_no"] == "MAT-001"

        # draft → approved → issued → completed
        for target in ["approved", "issued", "completed"]:
            resp = client.patch(f"/api/erp/material-issues/{mi['id']}", json={"status": target})
            assert resp.status_code == 200, f"Failed: {target}"

    def test_wo_to_mi_traceability(self, client):
        wo_id, pid = self._setup(client)
        client.post("/api/erp/material-issues", json={
            "issue_no": "MI-001", "work_order_id": wo_id,
            "items": [{"product_id": pid, "seq": 1, "requested_qty": 30}],
        })
        resp = client.get(f"/api/erp/material-issues?work_order_id={wo_id}")
        assert len(resp.json()) == 1
