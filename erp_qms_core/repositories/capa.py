from __future__ import annotations

from sqlalchemy.orm import Session

from ..models.capa import CAPA, CustomerComplaint


# ── CustomerComplaint ──────────────────────────────────

def list_complaints(
    session: Session,
    *,
    status: str | None = None,
    severity: str | None = None,
    complaint_type: str | None = None,
    customer_id: str | None = None,
    product_id: str | None = None,
    requires_capa: bool | None = None,
    lot_no: str | None = None,
) -> list[CustomerComplaint]:
    q = session.query(CustomerComplaint)
    if status:
        q = q.filter(CustomerComplaint.status == status)
    if severity:
        q = q.filter(CustomerComplaint.severity == severity)
    if complaint_type:
        q = q.filter(CustomerComplaint.complaint_type == complaint_type)
    if customer_id:
        q = q.filter(CustomerComplaint.customer_id == customer_id)
    if product_id:
        q = q.filter(CustomerComplaint.product_id == product_id)
    if requires_capa is not None:
        q = q.filter(CustomerComplaint.requires_capa == requires_capa)
    if lot_no:
        q = q.filter(CustomerComplaint.lot_no == lot_no)
    return q.order_by(CustomerComplaint.complaint_no.desc()).all()


def get_complaint(session: Session, complaint_id: str) -> CustomerComplaint | None:
    return session.get(CustomerComplaint, complaint_id)


def get_complaint_by_no(session: Session, complaint_no: str) -> CustomerComplaint | None:
    return session.query(CustomerComplaint).filter(
        CustomerComplaint.complaint_no == complaint_no,
    ).first()


def create_complaint(session: Session, data: dict) -> CustomerComplaint:
    obj = CustomerComplaint(**data)
    session.add(obj)
    session.flush()
    return obj


def update_complaint(session: Session, complaint_id: str, data: dict) -> CustomerComplaint | None:
    obj = session.get(CustomerComplaint, complaint_id)
    if not obj:
        return None
    for k, v in data.items():
        if v is not None:
            setattr(obj, k, v)
    session.flush()
    return obj


def delete_complaint(session: Session, complaint_id: str) -> bool:
    obj = session.get(CustomerComplaint, complaint_id)
    if not obj:
        return False
    session.delete(obj)
    session.flush()
    return True


# ── CAPA ───────────────────────────────────────────────

def list_capas(
    session: Session,
    *,
    status: str | None = None,
    capa_type: str | None = None,
    source_type: str | None = None,
    severity: str | None = None,
    assigned_to: str | None = None,
    ncr_id: str | None = None,
    complaint_id: str | None = None,
    effectiveness_verified: bool | None = None,
) -> list[CAPA]:
    q = session.query(CAPA)
    if status:
        q = q.filter(CAPA.status == status)
    if capa_type:
        q = q.filter(CAPA.capa_type == capa_type)
    if source_type:
        q = q.filter(CAPA.source_type == source_type)
    if severity:
        q = q.filter(CAPA.severity == severity)
    if assigned_to:
        q = q.filter(CAPA.assigned_to == assigned_to)
    if ncr_id:
        q = q.filter(CAPA.ncr_id == ncr_id)
    if complaint_id:
        q = q.filter(CAPA.complaint_id == complaint_id)
    if effectiveness_verified is not None:
        q = q.filter(CAPA.effectiveness_verified == effectiveness_verified)
    return q.order_by(CAPA.capa_no.desc()).all()


def get_capa(session: Session, capa_id: str) -> CAPA | None:
    return session.get(CAPA, capa_id)


def get_capa_by_no(session: Session, capa_no: str) -> CAPA | None:
    return session.query(CAPA).filter(CAPA.capa_no == capa_no).first()


def create_capa(session: Session, data: dict) -> CAPA:
    obj = CAPA(**data)
    session.add(obj)
    session.flush()
    return obj


def update_capa(session: Session, capa_id: str, data: dict) -> CAPA | None:
    obj = session.get(CAPA, capa_id)
    if not obj:
        return None
    for k, v in data.items():
        if v is not None:
            setattr(obj, k, v)
    session.flush()
    return obj


def delete_capa(session: Session, capa_id: str) -> bool:
    obj = session.get(CAPA, capa_id)
    if not obj:
        return False
    session.delete(obj)
    session.flush()
    return True
