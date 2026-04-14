from __future__ import annotations

from sqlalchemy.orm import Session

from ..models.order import SalesOrder, SalesOrderItem, WorkOrder


# ── SalesOrder ──────────────────────────────────────────

def list_sales_orders(session: Session, *, status: str | None = None, customer_id: str | None = None) -> list[SalesOrder]:
    q = session.query(SalesOrder)
    if status:
        q = q.filter(SalesOrder.status == status)
    if customer_id:
        q = q.filter(SalesOrder.customer_id == customer_id)
    return q.order_by(SalesOrder.order_no.desc()).all()


def get_sales_order(session: Session, order_id: str) -> SalesOrder | None:
    return session.get(SalesOrder, order_id)


def get_sales_order_by_no(session: Session, order_no: str) -> SalesOrder | None:
    return session.query(SalesOrder).filter(SalesOrder.order_no == order_no).first()


def create_sales_order(session: Session, data: dict, items: list[dict] | None = None) -> SalesOrder:
    order = SalesOrder(**data)
    session.add(order)
    session.flush()
    total = 0.0
    if items:
        for item_data in items:
            line_amount = item_data.get("quantity", 0) * item_data.get("unit_price", 0)
            item_data["line_amount"] = line_amount
            item = SalesOrderItem(order_id=order.id, **item_data)
            session.add(item)
            total += line_amount
    order.total_amount = total
    session.flush()
    return order


def update_sales_order(session: Session, order_id: str, data: dict, items: list[dict] | None = None) -> SalesOrder | None:
    order = session.get(SalesOrder, order_id)
    if not order:
        return None
    for k, v in data.items():
        if v is not None:
            setattr(order, k, v)
    if items is not None:
        for old in list(order.items):
            session.delete(old)
        session.flush()
        total = 0.0
        for item_data in items:
            line_amount = item_data.get("quantity", 0) * item_data.get("unit_price", 0)
            item_data["line_amount"] = line_amount
            item = SalesOrderItem(order_id=order.id, **item_data)
            session.add(item)
            total += line_amount
        order.total_amount = total
        session.flush()
        session.expire(order, ["items"])
    session.flush()
    return order


def delete_sales_order(session: Session, order_id: str) -> bool:
    order = session.get(SalesOrder, order_id)
    if not order:
        return False
    session.delete(order)
    session.flush()
    return True


# ── WorkOrder ───────────────────────────────────────────

def list_work_orders(
    session: Session,
    *,
    status: str | None = None,
    sales_order_id: str | None = None,
    product_id: str | None = None,
    lot_no: str | None = None,
) -> list[WorkOrder]:
    q = session.query(WorkOrder)
    if status:
        q = q.filter(WorkOrder.status == status)
    if sales_order_id:
        q = q.filter(WorkOrder.sales_order_id == sales_order_id)
    if product_id:
        q = q.filter(WorkOrder.product_id == product_id)
    if lot_no:
        q = q.filter(WorkOrder.lot_no == lot_no)
    return q.order_by(WorkOrder.wo_no.desc()).all()


def get_work_order(session: Session, wo_id: str) -> WorkOrder | None:
    return session.get(WorkOrder, wo_id)


def get_work_order_by_no(session: Session, wo_no: str) -> WorkOrder | None:
    return session.query(WorkOrder).filter(WorkOrder.wo_no == wo_no).first()


def create_work_order(session: Session, data: dict) -> WorkOrder:
    wo = WorkOrder(**data)
    session.add(wo)
    session.flush()
    return wo


def update_work_order(session: Session, wo_id: str, data: dict) -> WorkOrder | None:
    wo = session.get(WorkOrder, wo_id)
    if not wo:
        return None
    for k, v in data.items():
        if v is not None:
            setattr(wo, k, v)
    session.flush()
    return wo


def delete_work_order(session: Session, wo_id: str) -> bool:
    wo = session.get(WorkOrder, wo_id)
    if not wo:
        return False
    session.delete(wo)
    session.flush()
    return True
