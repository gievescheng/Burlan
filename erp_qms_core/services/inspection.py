from __future__ import annotations

from sqlalchemy.orm import Session

from ..domain.transitions import validate_status_transition
from ..repositories import inspection as repo

VALID_DISPOSITIONS = {"", "release", "hold", "reject", "concession", "rework"}
VALID_INSPECTION_TYPES = {"incoming", "in_process", "final", "random"}


def list_inspection_lots(
    session: Session,
    status: str | None = None,
    disposition: str | None = None,
    inspection_type: str | None = None,
    work_order_id: str | None = None,
    product_id: str | None = None,
    source_lot_no: str | None = None,
) -> list[dict]:
    rows = repo.list_inspection_lots(
        session,
        status=status,
        disposition=disposition,
        inspection_type=inspection_type,
        work_order_id=work_order_id,
        product_id=product_id,
        source_lot_no=source_lot_no,
    )
    return [_lot_to_dict(r) for r in rows]


def get_inspection_lot(session: Session, lot_id: str) -> dict | None:
    row = repo.get_inspection_lot(session, lot_id)
    return _lot_to_dict(row) if row else None


def create_inspection_lot(session: Session, data: dict) -> dict:
    if repo.get_inspection_lot_by_no(session, data["lot_no"]):
        raise ValueError(f"Inspection lot '{data['lot_no']}' already exists")
    if data.get("inspection_type") and data["inspection_type"] not in VALID_INSPECTION_TYPES:
        raise ValueError(
            f"Invalid inspection_type. Allowed: {sorted(VALID_INSPECTION_TYPES)}"
        )
    results = data.pop("results", [])
    lot = repo.create_inspection_lot(session, data, results=results)
    # 全部結果均 pass 可自動進入 in_progress（保持 pending 也允許）
    return _lot_to_dict(lot)


def update_inspection_lot(session: Session, lot_id: str, data: dict) -> dict | None:
    current = repo.get_inspection_lot(session, lot_id)
    if not current:
        return None
    # 狀態流轉檢查
    if "status" in data and data["status"] is not None:
        err = validate_status_transition(
            "inspection_lot", current.status, data["status"],
        )
        if err:
            raise ValueError(err)
    # disposition 檢查
    if "disposition" in data and data["disposition"] is not None:
        if data["disposition"] not in VALID_DISPOSITIONS:
            raise ValueError(
                f"Invalid disposition. Allowed: {sorted(VALID_DISPOSITIONS - {''})}"
            )
    if "inspection_type" in data and data["inspection_type"] is not None:
        if data["inspection_type"] not in VALID_INSPECTION_TYPES:
            raise ValueError(
                f"Invalid inspection_type. Allowed: {sorted(VALID_INSPECTION_TYPES)}"
            )
    results = data.pop("results", None)
    row = repo.update_inspection_lot(session, lot_id, data, results=results)
    return _lot_to_dict(row) if row else None


def delete_inspection_lot(session: Session, lot_id: str) -> bool:
    return repo.delete_inspection_lot(session, lot_id)


def _row_to_dict(row) -> dict:
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}


def _lot_to_dict(lot) -> dict:
    d = _row_to_dict(lot)
    d["results"] = [_row_to_dict(r) for r in lot.results]
    return d
