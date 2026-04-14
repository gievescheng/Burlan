from __future__ import annotations

from sqlalchemy.orm import Session

from ..domain.transitions import validate_status_transition
from ..repositories import order as repo


# ── SalesOrder ──────────────────────────────────────────

def list_sales_orders(session: Session, status: str | None = None, customer_id: str | None = None) -> list[dict]:
    rows = repo.list_sales_orders(session, status=status, customer_id=customer_id)
    return [_so_to_dict(r) for r in rows]


def get_sales_order(session: Session, order_id: str) -> dict | None:
    row = repo.get_sales_order(session, order_id)
    return _so_to_dict(row) if row else None


def create_sales_order(session: Session, data: dict) -> dict:
    if repo.get_sales_order_by_no(session, data["order_no"]):
        raise ValueError(f"Sales order '{data['order_no']}' already exists")
    items = data.pop("items", [])
    return _so_to_dict(repo.create_sales_order(session, data, items=items))


def update_sales_order(session: Session, order_id: str, data: dict) -> dict | None:
    if "status" in data and data["status"] is not None:
        existing = repo.get_sales_order(session, order_id)
        if not existing:
            return None
        err = validate_status_transition("sales_order", existing.status, data["status"])
        if err:
            raise ValueError(err)
    items = data.pop("items", None)
    row = repo.update_sales_order(session, order_id, data, items=items)
    return _so_to_dict(row) if row else None


def delete_sales_order(session: Session, order_id: str) -> bool:
    return repo.delete_sales_order(session, order_id)


# ── WorkOrder ───────────────────────────────────────────

def list_work_orders(
    session: Session,
    status: str | None = None,
    sales_order_id: str | None = None,
    product_id: str | None = None,
    lot_no: str | None = None,
) -> list[dict]:
    rows = repo.list_work_orders(
        session, status=status, sales_order_id=sales_order_id,
        product_id=product_id, lot_no=lot_no,
    )
    return [_row_to_dict(r) for r in rows]


def get_work_order(session: Session, wo_id: str) -> dict | None:
    row = repo.get_work_order(session, wo_id)
    return _row_to_dict(row) if row else None


def create_work_order(session: Session, data: dict) -> dict:
    if repo.get_work_order_by_no(session, data["wo_no"]):
        raise ValueError(f"Work order '{data['wo_no']}' already exists")
    return _row_to_dict(repo.create_work_order(session, data))


def update_work_order(session: Session, wo_id: str, data: dict) -> dict | None:
    if "status" in data and data["status"] is not None:
        existing = repo.get_work_order(session, wo_id)
        if not existing:
            return None
        err = validate_status_transition("work_order", existing.status, data["status"])
        if err:
            raise ValueError(err)
    row = repo.update_work_order(session, wo_id, data)
    return _row_to_dict(row) if row else None


def delete_work_order(session: Session, wo_id: str) -> bool:
    return repo.delete_work_order(session, wo_id)


# ── helpers ─────────────────────────────────────────────

def _row_to_dict(row) -> dict:
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}


def _so_to_dict(order) -> dict:
    d = _row_to_dict(order)
    d["items"] = [_row_to_dict(i) for i in order.items]
    return d
