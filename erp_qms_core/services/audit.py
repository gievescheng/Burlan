from __future__ import annotations

from sqlalchemy.orm import Session

from ..domain.transitions import validate_status_transition
from ..repositories import audit as repo
from ..repositories import capa as capa_repo

VALID_AUDIT_TYPES = {"planned", "unannounced", "follow_up", "special"}
VALID_AUDIT_SCOPES = {"process", "department", "clause", "full_system"}
VALID_FINDING_TYPES = {"major_nc", "minor_nc", "observation", "opportunity"}


# ── InternalAudit ──────────────────────────────────────

def list_audits(
    session: Session,
    status: str | None = None,
    audit_type: str | None = None,
    scope: str | None = None,
    department: str | None = None,
) -> list[dict]:
    rows = repo.list_audits(
        session, status=status, audit_type=audit_type,
        scope=scope, department=department,
    )
    return [_audit_to_dict(r) for r in rows]


def get_audit(session: Session, audit_id: str) -> dict | None:
    row = repo.get_audit(session, audit_id)
    return _audit_to_dict(row) if row else None


def create_audit(session: Session, data: dict) -> dict:
    if repo.get_audit_by_no(session, data["audit_no"]):
        raise ValueError(f"Audit '{data['audit_no']}' already exists")
    _validate_audit_enums(data)
    return _audit_to_dict(repo.create_audit(session, data))


def update_audit(session: Session, audit_id: str, data: dict) -> dict | None:
    current = repo.get_audit(session, audit_id)
    if not current:
        return None
    _validate_audit_enums(data)
    if "status" in data and data["status"] is not None:
        err = validate_status_transition(
            "internal_audit", current.status, data["status"],
        )
        if err:
            raise ValueError(err)
        # ISO §9.2.2 e) 稽核結案前所有發現必須已 closed 或 cancelled
        if data["status"] == "closed":
            open_findings = [
                f for f in repo.list_findings(session, audit_id=audit_id)
                if f.status not in {"closed", "cancelled"}
            ]
            if open_findings:
                raise ValueError(
                    f"Cannot close audit: {len(open_findings)} finding(s) "
                    f"still open (ISO 9001 §9.2.2 e)"
                )
    row = repo.update_audit(session, audit_id, data)
    return _audit_to_dict(row) if row else None


def delete_audit(session: Session, audit_id: str) -> bool:
    return repo.delete_audit(session, audit_id)


# ── AuditFinding ───────────────────────────────────────

def list_findings(
    session: Session,
    audit_id: str | None = None,
    status: str | None = None,
    finding_type: str | None = None,
    requires_capa: bool | None = None,
    clause: str | None = None,
) -> list[dict]:
    rows = repo.list_findings(
        session, audit_id=audit_id, status=status,
        finding_type=finding_type, requires_capa=requires_capa, clause=clause,
    )
    return [_finding_to_dict(r) for r in rows]


def get_finding(session: Session, finding_id: str) -> dict | None:
    row = repo.get_finding(session, finding_id)
    return _finding_to_dict(row) if row else None


def create_finding(session: Session, data: dict) -> dict:
    if not repo.get_audit(session, data["audit_id"]):
        raise ValueError(f"Audit '{data['audit_id']}' not found")
    if repo.get_finding_by_no(session, data["finding_no"]):
        raise ValueError(f"Finding '{data['finding_no']}' already exists")
    _validate_finding_enums(data)
    # major_nc 自動觸發 requires_capa（ISO §9.2.2 e) 矯正要求）
    if data.get("finding_type") == "major_nc":
        data["requires_capa"] = True
    if data.get("capa_id"):
        if not capa_repo.get_capa(session, data["capa_id"]):
            raise ValueError(f"CAPA '{data['capa_id']}' not found")
    obj = repo.create_finding(session, data)
    repo.recompute_audit_counts(session, data["audit_id"])
    return _finding_to_dict(obj)


def update_finding(session: Session, finding_id: str, data: dict) -> dict | None:
    current = repo.get_finding(session, finding_id)
    if not current:
        return None
    _validate_finding_enums(data)
    if "finding_type" in data and data["finding_type"] == "major_nc":
        data["requires_capa"] = True
    if data.get("capa_id"):
        if not capa_repo.get_capa(session, data["capa_id"]):
            raise ValueError(f"CAPA '{data['capa_id']}' not found")
    if "status" in data and data["status"] is not None:
        err = validate_status_transition(
            "audit_finding", current.status, data["status"],
        )
        if err:
            raise ValueError(err)
        # 結案必須已驗證
        if data["status"] == "closed":
            verified = (
                data.get("verified_by") or current.verified_by
            )
            if not verified:
                raise ValueError(
                    "Cannot close finding: verified_by must be set "
                    "(ISO 9001 §9.2.2 e)"
                )
    row = repo.update_finding(session, finding_id, data)
    if row:
        repo.recompute_audit_counts(session, row.audit_id)
    return _finding_to_dict(row) if row else None


def delete_finding(session: Session, finding_id: str) -> bool:
    row = repo.get_finding(session, finding_id)
    if not row:
        return False
    audit_id = row.audit_id
    ok = repo.delete_finding(session, finding_id)
    if ok:
        repo.recompute_audit_counts(session, audit_id)
    return ok


# ── helpers ────────────────────────────────────────────

def _validate_audit_enums(data: dict) -> None:
    if "audit_type" in data and data["audit_type"] is not None:
        if data["audit_type"] not in VALID_AUDIT_TYPES:
            raise ValueError(
                f"Invalid audit_type. Allowed: {sorted(VALID_AUDIT_TYPES)}"
            )
    if "scope" in data and data["scope"] is not None:
        if data["scope"] not in VALID_AUDIT_SCOPES:
            raise ValueError(f"Invalid scope. Allowed: {sorted(VALID_AUDIT_SCOPES)}")


def _validate_finding_enums(data: dict) -> None:
    if "finding_type" in data and data["finding_type"] is not None:
        if data["finding_type"] not in VALID_FINDING_TYPES:
            raise ValueError(
                f"Invalid finding_type. Allowed: {sorted(VALID_FINDING_TYPES)}"
            )


def _audit_to_dict(row) -> dict:
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}


def _finding_to_dict(row) -> dict:
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}
