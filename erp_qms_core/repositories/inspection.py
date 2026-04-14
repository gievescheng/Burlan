from __future__ import annotations

from sqlalchemy.orm import Session

from ..models.inspection import InspectionLot, InspectionResult


def list_inspection_lots(
    session: Session,
    *,
    status: str | None = None,
    disposition: str | None = None,
    inspection_type: str | None = None,
    work_order_id: str | None = None,
    product_id: str | None = None,
    source_lot_no: str | None = None,
) -> list[InspectionLot]:
    q = session.query(InspectionLot)
    if status:
        q = q.filter(InspectionLot.status == status)
    if disposition:
        q = q.filter(InspectionLot.disposition == disposition)
    if inspection_type:
        q = q.filter(InspectionLot.inspection_type == inspection_type)
    if work_order_id:
        q = q.filter(InspectionLot.work_order_id == work_order_id)
    if product_id:
        q = q.filter(InspectionLot.product_id == product_id)
    if source_lot_no:
        q = q.filter(InspectionLot.source_lot_no == source_lot_no)
    return q.order_by(InspectionLot.lot_no.desc()).all()


def get_inspection_lot(session: Session, lot_id: str) -> InspectionLot | None:
    return session.get(InspectionLot, lot_id)


def get_inspection_lot_by_no(session: Session, lot_no: str) -> InspectionLot | None:
    return session.query(InspectionLot).filter(InspectionLot.lot_no == lot_no).first()


def create_inspection_lot(
    session: Session, data: dict, results: list[dict] | None = None,
) -> InspectionLot:
    lot = InspectionLot(**data)
    session.add(lot)
    session.flush()
    if results:
        for r in results:
            r_obj = InspectionResult(inspection_lot_id=lot.id, **r)
            _auto_judge(r_obj)
            session.add(r_obj)
        session.flush()
    _recompute_lot_qty(lot)
    session.flush()
    return lot


def update_inspection_lot(
    session: Session, lot_id: str, data: dict, results: list[dict] | None = None,
) -> InspectionLot | None:
    lot = session.get(InspectionLot, lot_id)
    if not lot:
        return None
    for k, v in data.items():
        if v is not None:
            setattr(lot, k, v)
    if results is not None:
        for old in list(lot.results):
            session.delete(old)
        session.flush()
        for r in results:
            r_obj = InspectionResult(inspection_lot_id=lot.id, **r)
            _auto_judge(r_obj)
            session.add(r_obj)
        session.flush()
        session.expire(lot, ["results"])
    _recompute_lot_qty(lot)
    session.flush()
    return lot


def delete_inspection_lot(session: Session, lot_id: str) -> bool:
    lot = session.get(InspectionLot, lot_id)
    if not lot:
        return False
    session.delete(lot)
    session.flush()
    return True


def _auto_judge(r: InspectionResult) -> None:
    """根據 LSL/USL 或 actual_text 自動判定 pass/fail（若未明確指定 fail）。"""
    if r.result and r.result not in ("pass",):
        return
    text = (r.actual_text or "").strip().lower()
    if text in ("ng", "fail", "reject", "nok"):
        r.result = "fail"
        return
    if r.actual_value is not None:
        if r.lsl is not None and r.actual_value < r.lsl:
            r.result = "fail"
            return
        if r.usl is not None and r.actual_value > r.usl:
            r.result = "fail"
            return
    r.result = "pass"


def _recompute_lot_qty(lot: InspectionLot) -> None:
    """根據結果列表重算 accept_qty / reject_qty（若未明確設定）。"""
    if not lot.results:
        return
    fail_qty = sum((r.defect_qty or 0.0) for r in lot.results if r.result == "fail")
    if fail_qty > 0 and lot.reject_qty == 0.0:
        lot.reject_qty = fail_qty
    if lot.sample_size > 0 and lot.accept_qty == 0.0 and lot.reject_qty <= lot.sample_size:
        lot.accept_qty = lot.sample_size - lot.reject_qty
