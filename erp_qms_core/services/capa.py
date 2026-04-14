from __future__ import annotations

from sqlalchemy.orm import Session

from ..domain.transitions import validate_status_transition
from ..repositories import capa as repo

VALID_COMPLAINT_TYPES = {"quality", "delivery", "service", "documentation", "other"}
VALID_COMPLAINT_CHANNELS = {"email", "phone", "portal", "visit", "other"}
VALID_SEVERITIES = {"critical", "major", "minor"}
VALID_CAPA_TYPES = {"corrective", "preventive"}
VALID_SOURCE_TYPES = {"ncr", "complaint", "audit", "management_review", "other"}
VALID_ROOT_CAUSE_METHODS = {"5why", "ishikawa", "8d", "fmea", "other"}


# ── CustomerComplaint ──────────────────────────────────

def list_complaints(
    session: Session,
    status: str | None = None,
    severity: str | None = None,
    complaint_type: str | None = None,
    customer_id: str | None = None,
    product_id: str | None = None,
    requires_capa: bool | None = None,
    lot_no: str | None = None,
) -> list[dict]:
    rows = repo.list_complaints(
        session,
        status=status, severity=severity, complaint_type=complaint_type,
        customer_id=customer_id, product_id=product_id,
        requires_capa=requires_capa, lot_no=lot_no,
    )
    return [_row_to_dict(r) for r in rows]


def get_complaint(session: Session, complaint_id: str) -> dict | None:
    row = repo.get_complaint(session, complaint_id)
    return _row_to_dict(row) if row else None


def create_complaint(session: Session, data: dict) -> dict:
    if repo.get_complaint_by_no(session, data["complaint_no"]):
        raise ValueError(f"Complaint '{data['complaint_no']}' already exists")
    if data.get("complaint_type") and data["complaint_type"] not in VALID_COMPLAINT_TYPES:
        raise ValueError(f"Invalid complaint_type. Allowed: {sorted(VALID_COMPLAINT_TYPES)}")
    if data.get("severity") and data["severity"] not in VALID_SEVERITIES:
        raise ValueError(f"Invalid severity. Allowed: {sorted(VALID_SEVERITIES)}")
    if data.get("channel") and data["channel"] not in VALID_COMPLAINT_CHANNELS:
        raise ValueError(f"Invalid channel. Allowed: {sorted(VALID_COMPLAINT_CHANNELS)}")
    # critical 客訴強制觸發 CAPA（ISO 10.2 — 對顧客嚴重抱怨須矯正措施）
    if data.get("severity") == "critical":
        data["requires_capa"] = True
    return _row_to_dict(repo.create_complaint(session, data))


def update_complaint(session: Session, complaint_id: str, data: dict) -> dict | None:
    current = repo.get_complaint(session, complaint_id)
    if not current:
        return None
    if "status" in data and data["status"] is not None:
        err = validate_status_transition(
            "customer_complaint", current.status, data["status"],
        )
        if err:
            raise ValueError(err)
    if "severity" in data and data["severity"] is not None:
        if data["severity"] not in VALID_SEVERITIES:
            raise ValueError(f"Invalid severity. Allowed: {sorted(VALID_SEVERITIES)}")
        if data["severity"] == "critical":
            data["requires_capa"] = True
    if "complaint_type" in data and data["complaint_type"] is not None:
        if data["complaint_type"] not in VALID_COMPLAINT_TYPES:
            raise ValueError(
                f"Invalid complaint_type. Allowed: {sorted(VALID_COMPLAINT_TYPES)}"
            )
    if "channel" in data and data["channel"] is not None:
        if data["channel"] not in VALID_COMPLAINT_CHANNELS:
            raise ValueError(
                f"Invalid channel. Allowed: {sorted(VALID_COMPLAINT_CHANNELS)}"
            )
    row = repo.update_complaint(session, complaint_id, data)
    return _row_to_dict(row) if row else None


def delete_complaint(session: Session, complaint_id: str) -> bool:
    return repo.delete_complaint(session, complaint_id)


# ── CAPA ───────────────────────────────────────────────

def list_capas(
    session: Session,
    status: str | None = None,
    capa_type: str | None = None,
    source_type: str | None = None,
    severity: str | None = None,
    assigned_to: str | None = None,
    ncr_id: str | None = None,
    complaint_id: str | None = None,
    effectiveness_verified: bool | None = None,
) -> list[dict]:
    rows = repo.list_capas(
        session, status=status, capa_type=capa_type, source_type=source_type,
        severity=severity, assigned_to=assigned_to,
        ncr_id=ncr_id, complaint_id=complaint_id,
        effectiveness_verified=effectiveness_verified,
    )
    return [_row_to_dict(r) for r in rows]


def get_capa(session: Session, capa_id: str) -> dict | None:
    row = repo.get_capa(session, capa_id)
    return _row_to_dict(row) if row else None


def create_capa(session: Session, data: dict) -> dict:
    if repo.get_capa_by_no(session, data["capa_no"]):
        raise ValueError(f"CAPA '{data['capa_no']}' already exists")
    _validate_capa_enums(data)
    return _row_to_dict(repo.create_capa(session, data))


def update_capa(session: Session, capa_id: str, data: dict) -> dict | None:
    current = repo.get_capa(session, capa_id)
    if not current:
        return None
    if "status" in data and data["status"] is not None:
        err = validate_status_transition("capa", current.status, data["status"])
        if err:
            raise ValueError(err)
        # ISO §10.2.1 d) — 結案前必須驗證有效性
        target = data["status"]
        if target == "closed":
            verified = data.get("effectiveness_verified", current.effectiveness_verified)
            if not verified:
                raise ValueError(
                    "Cannot close CAPA: effectiveness_verified must be true (ISO 9001 §10.2.1 d)"
                )
    _validate_capa_enums(data)
    row = repo.update_capa(session, capa_id, data)
    return _row_to_dict(row) if row else None


def delete_capa(session: Session, capa_id: str) -> bool:
    return repo.delete_capa(session, capa_id)


# ── helpers ────────────────────────────────────────────

def _validate_capa_enums(data: dict) -> None:
    if "capa_type" in data and data["capa_type"] is not None:
        if data["capa_type"] not in VALID_CAPA_TYPES:
            raise ValueError(f"Invalid capa_type. Allowed: {sorted(VALID_CAPA_TYPES)}")
    if "source_type" in data and data["source_type"] is not None:
        if data["source_type"] not in VALID_SOURCE_TYPES:
            raise ValueError(f"Invalid source_type. Allowed: {sorted(VALID_SOURCE_TYPES)}")
    if "severity" in data and data["severity"] is not None:
        if data["severity"] not in VALID_SEVERITIES:
            raise ValueError(f"Invalid severity. Allowed: {sorted(VALID_SEVERITIES)}")
    if "root_cause_method" in data and data["root_cause_method"] is not None:
        if data["root_cause_method"] not in VALID_ROOT_CAUSE_METHODS:
            raise ValueError(
                f"Invalid root_cause_method. Allowed: {sorted(VALID_ROOT_CAUSE_METHODS)}"
            )


def _row_to_dict(row) -> dict:
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}
