"""Tests for Sales Order and Work Order (models, services, API)."""
from __future__ import annotations

import pytest

from erp_qms_core.domain.transitions import validate_status_transition
from erp_qms_core.repositories import master as master_repo
from erp_qms_core.repositories import order as order_repo


# ── Domain transitions ─────────────────────────────────

class TestOrderTransitions:
    def test_so_draft_to_confirmed(self):
        assert validate_status_transition("sales_order", "draft", "confirmed") is None

    def test_so_draft_to_completed_blocked(self):
        err = validate_status_transition("sales_order", "draft", "completed")
        assert err is not None
        assert "Cannot transition" in err

    def test_wo_in_progress_to_on_hold(self):
        assert validate_status_transition("work_order", "in_progress", "on_hold") is None

    def test_wo_completed_cannot_revert(self):
        err = validate_status_transition("work_order", "completed", "in_progress")
        assert err is not None

    def test_wo_closed_is_terminal(self):
        err = validate_status_transition("work_order", "closed", "draft")
        assert err is not None


# ── Repository tests ────────────────────────────────────

class TestSalesOrderRepository:
    def _make_customer(self, session):
        return master_repo.create_customer(session, {"customer_code": "C001", "name": "Acme"})

    def _make_product(self, session):
        return master_repo.create_product(session, {"product_code": "P001", "name": "Widget"})

    def test_create_with_items(self, db_session):
        cust = self._make_customer(db_session)
        prod = self._make_product(db_session)
        db_session.flush()

        so = order_repo.create_sales_order(db_session, {
            "order_no": "SO-001",
            "customer_id": cust.id,
        }, items=[
            {"product_id": prod.id, "seq": 1, "quantity": 10, "unit_price": 100},
        ])
        db_session.flush()

        assert so.order_no == "SO-001"
        assert len(so.items) == 1
        assert so.items[0].line_amount == 1000.0
        assert so.total_amount == 1000.0

    def test_update_replaces_items(self, db_session):
        cust = self._make_customer(db_session)
        prod = self._make_product(db_session)
        db_session.flush()

        so = order_repo.create_sales_order(db_session, {
            "order_no": "SO-001",
            "customer_id": cust.id,
        }, items=[
            {"product_id": prod.id, "seq": 1, "quantity": 5, "unit_price": 200},
        ])
        db_session.flush()

        updated = order_repo.update_sales_order(db_session, so.id, {}, items=[
            {"product_id": prod.id, "seq": 1, "quantity": 20, "unit_price": 50},
        ])
        db_session.flush()
        assert updated.total_amount == 1000.0
        assert len(updated.items) == 1
        assert updated.items[0].quantity == 20

    def test_delete_cascades(self, db_session):
        cust = self._make_customer(db_session)
        prod = self._make_product(db_session)
        db_session.flush()

        so = order_repo.create_sales_order(db_session, {
            "order_no": "SO-001",
            "customer_id": cust.id,
        }, items=[
            {"product_id": prod.id, "seq": 1, "quantity": 1, "unit_price": 1},
        ])
        db_session.flush()
        assert order_repo.delete_sales_order(db_session, so.id) is True
        assert order_repo.get_sales_order(db_session, so.id) is None


class TestWorkOrderRepository:
    def _make_product(self, session):
        return master_repo.create_product(session, {"product_code": "P001", "name": "Widget"})

    def test_create_and_get(self, db_session):
        prod = self._make_product(db_session)
        db_session.flush()

        wo = order_repo.create_work_order(db_session, {
            "wo_no": "WO-001",
            "product_id": prod.id,
            "planned_qty": 100,
            "lot_no": "LOT-2026-001",
        })
        db_session.flush()
        assert wo.wo_no == "WO-001"
        assert wo.lot_no == "LOT-2026-001"
        assert wo.status == "draft"

    def test_filter_by_lot(self, db_session):
        prod = self._make_product(db_session)
        db_session.flush()

        order_repo.create_work_order(db_session, {"wo_no": "WO-001", "product_id": prod.id, "planned_qty": 10, "lot_no": "LOT-A"})
        order_repo.create_work_order(db_session, {"wo_no": "WO-002", "product_id": prod.id, "planned_qty": 20, "lot_no": "LOT-B"})
        db_session.flush()

        results = order_repo.list_work_orders(db_session, lot_no="LOT-A")
        assert len(results) == 1
        assert results[0].wo_no == "WO-001"

    def test_link_to_sales_order(self, db_session):
        cust = master_repo.create_customer(db_session, {"customer_code": "C001", "name": "Acme"})
        prod = self._make_product(db_session)
        db_session.flush()

        so = order_repo.create_sales_order(db_session, {
            "order_no": "SO-001",
            "customer_id": cust.id,
        }, items=[
            {"product_id": prod.id, "seq": 1, "quantity": 50, "unit_price": 10},
        ])
        db_session.flush()

        wo = order_repo.create_work_order(db_session, {
            "wo_no": "WO-001",
            "product_id": prod.id,
            "sales_order_id": so.id,
            "sales_order_item_id": so.items[0].id,
            "planned_qty": 50,
        })
        db_session.flush()
        assert wo.sales_order_id == so.id
        assert wo.sales_order_item_id == so.items[0].id


# ── API tests ───────────────────────────────────────────

class TestSalesOrderAPI:
    def _setup_master_data(self, client):
        c = client.post("/api/erp/customers", json={"customer_code": "C001", "name": "Acme"})
        p = client.post("/api/erp/products", json={"product_code": "P001", "name": "Widget"})
        return c.json()["id"], p.json()["id"]

    def test_full_lifecycle(self, client):
        cid, pid = self._setup_master_data(client)

        # 建立
        resp = client.post("/api/erp/sales-orders", json={
            "order_no": "SO-001",
            "customer_id": cid,
            "items": [{"product_id": pid, "seq": 1, "quantity": 10, "unit_price": 100}],
        })
        assert resp.status_code == 201
        so = resp.json()
        assert so["order_no"] == "SO-001"
        assert so["status"] == "draft"
        assert so["total_amount"] == 1000.0
        assert len(so["items"]) == 1

        # 狀態轉換: draft → confirmed
        resp = client.patch(f"/api/erp/sales-orders/{so['id']}", json={"status": "confirmed"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "confirmed"

        # 非法轉換: confirmed → closed (跳過 in_production + completed)
        resp = client.patch(f"/api/erp/sales-orders/{so['id']}", json={"status": "closed"})
        assert resp.status_code == 422

    def test_duplicate_order_no(self, client):
        cid, _ = self._setup_master_data(client)
        client.post("/api/erp/sales-orders", json={"order_no": "SO-001", "customer_id": cid})
        resp = client.post("/api/erp/sales-orders", json={"order_no": "SO-001", "customer_id": cid})
        assert resp.status_code == 409


class TestWorkOrderAPI:
    def _setup(self, client):
        c = client.post("/api/erp/customers", json={"customer_code": "C001", "name": "Acme"})
        p = client.post("/api/erp/products", json={"product_code": "P001", "name": "Widget"})
        return c.json()["id"], p.json()["id"]

    def test_create_and_transition(self, client):
        _, pid = self._setup(client)

        resp = client.post("/api/erp/work-orders", json={
            "wo_no": "WO-001",
            "product_id": pid,
            "planned_qty": 100,
            "lot_no": "LOT-2026-001",
        })
        assert resp.status_code == 201
        wo = resp.json()
        assert wo["status"] == "draft"

        # draft → released → in_progress → on_hold → in_progress → completed → closed
        for target in ["released", "in_progress", "on_hold", "in_progress", "completed", "closed"]:
            resp = client.patch(f"/api/erp/work-orders/{wo['id']}", json={"status": target})
            assert resp.status_code == 200, f"Failed transition to {target}: {resp.json()}"
            assert resp.json()["status"] == target

    def test_closed_is_terminal(self, client):
        _, pid = self._setup(client)
        resp = client.post("/api/erp/work-orders", json={
            "wo_no": "WO-001", "product_id": pid, "planned_qty": 10,
        })
        wo_id = resp.json()["id"]

        for target in ["released", "in_progress", "completed", "closed"]:
            client.patch(f"/api/erp/work-orders/{wo_id}", json={"status": target})

        resp = client.patch(f"/api/erp/work-orders/{wo_id}", json={"status": "draft"})
        assert resp.status_code == 422

    def test_so_to_wo_traceability(self, client):
        cid, pid = self._setup(client)

        so_resp = client.post("/api/erp/sales-orders", json={
            "order_no": "SO-001",
            "customer_id": cid,
            "items": [{"product_id": pid, "seq": 1, "quantity": 50, "unit_price": 10}],
        })
        so = so_resp.json()
        item_id = so["items"][0]["id"]

        wo_resp = client.post("/api/erp/work-orders", json={
            "wo_no": "WO-001",
            "product_id": pid,
            "sales_order_id": so["id"],
            "sales_order_item_id": item_id,
            "planned_qty": 50,
            "lot_no": "LOT-001",
        })
        assert wo_resp.status_code == 201
        wo = wo_resp.json()
        assert wo["sales_order_id"] == so["id"]
        assert wo["sales_order_item_id"] == item_id

        # 依 SO 過濾 WO
        resp = client.get(f"/api/erp/work-orders?sales_order_id={so['id']}")
        assert len(resp.json()) == 1
