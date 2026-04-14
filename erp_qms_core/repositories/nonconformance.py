from __future__ import annotations

from sqlalchemy.orm import Session

from ..models.nonconformance import NCR, ReworkOrder


# ── NCR ────────────────────────────────────────────────

def list_ncrs(
    session: Session,
    *,
    status: str | None = None,
    severity: str | None = None,
    category: str | None = None,
    disposition: str | None = None,
    work_order_id: str | None = None,
    product_id: str | None = None,
    inspection_lot_id: str | None = None,
    requires_capa: bool | None = None,
    lot_no: str | None = None,
) -> list[NCR]:
    q = session.query(NCR)
    if status:
        q = q.filter(NCR.status == status)
    if severity:
        q = q.filter(NCR.severity == severity)
    if category:
        q = q.filter(NCR.category == category)
    if disposition:
        q = q.filter(NCR.disposition == disposition)
    if work_order_id:
        q = q.filter(NCR.work_order_id == work_order_id)
    if product_id:
        q = q.filter(NCR.product_id == product_id)
    if inspection_lot_id:
        q = q.filter(NCR.inspection_lot_id == inspection_lot_id)
    if requires_capa is not None:
        q = q.filter(NCR.requires_capa == requires_capa)
    if lot_no:
        q = q.filter(NCR.lot_no == lot_no)
    return q.order_by(NCR.ncr_no.desc()).all()


def get_ncr(session: Session, ncr_id: str) -> NCR | None:
    return session.get(NCR, ncr_id)


def get_ncr_by_no(session: Session, ncr_no: str) -> NCR | None:
    return session.query(NCR).filter(NCR.ncr_no == ncr_no).first()


def create_ncr(session: Session, data: dict) -> NCR:
    ncr = NCR(**data)
    session.add(ncr)
    session.flush()
    return ncr


def update_ncr(session: Session, ncr_id: str, data: dict) -> NCR | None:
    ncr = session.get(NCR, ncr_id)
    if not ncr:
        return None
    for k, v in data.items():
        if v is not None:
            setattr(ncr, k, v)
    session.flush()
    return ncr


def delete_ncr(session: Session, ncr_id: str) -> bool:
    ncr = session.get(NCR, ncr_id)
    if not ncr:
        return False
    session.delete(ncr)
    session.flush()
    return True


# ── ReworkOrder ────────────────────────────────────────

def list_rework_orders(
    session: Session,
    *,
    ncr_id: str | None = None,
    work_order_id: str | None = None,
    status: str | None = None,
    result: str | None = None,
) -> list[ReworkOrder]:
    q = session.query(ReworkOrder)
    if ncr_id:
        q = q.filter(ReworkOrder.ncr_id == ncr_id)
    if work_order_id:
        q = q.filter(ReworkOrder.work_order_id == work_order_id)
    if status:
        q = q.filter(ReworkOrder.status == status)
    if result:
        q = q.filter(ReworkOrder.result == result)
    return q.order_by(ReworkOrder.rework_no.desc()).all()


def get_rework_order(session: Session, rework_id: str) -> ReworkOrder | None:
    return session.get(ReworkOrder, rework_id)


def get_rework_order_by_no(session: Session, rework_no: str) -> ReworkOrder | None:
    return session.query(ReworkOrder).filter(ReworkOrder.rework_no == rework_no).first()


def create_rework_order(session: Session, ncr_id: str, data: dict) -> ReworkOrder:
    rw = ReworkOrder(ncr_id=ncr_id, **data)
    session.add(rw)
    session.flush()
    return rw


def update_rework_order(session: Session, rework_id: str, data: dict) -> ReworkOrder | None:
    rw = session.get(ReworkOrder, rework_id)
    if not rw:
        return None
    for k, v in data.items():
        if v is not None:
            setattr(rw, k, v)
    session.flush()
    return rw


def delete_rework_order(session: Session, rework_id: str) -> bool:
    rw = session.get(ReworkOrder, rework_id)
    if not rw:
        return False
    session.delete(rw)
    session.flush()
    return True
