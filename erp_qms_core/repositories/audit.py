from __future__ import annotations

from sqlalchemy.orm import Session

from ..models.audit import AuditFinding, InternalAudit


# ── InternalAudit ──────────────────────────────────────

def list_audits(
    session: Session,
    *,
    status: str | None = None,
    audit_type: str | None = None,
    scope: str | None = None,
    department: str | None = None,
) -> list[InternalAudit]:
    q = session.query(InternalAudit)
    if status:
        q = q.filter(InternalAudit.status == status)
    if audit_type:
        q = q.filter(InternalAudit.audit_type == audit_type)
    if scope:
        q = q.filter(InternalAudit.scope == scope)
    if department:
        q = q.filter(InternalAudit.department == department)
    return q.order_by(InternalAudit.audit_no.desc()).all()


def get_audit(session: Session, audit_id: str) -> InternalAudit | None:
    return session.get(InternalAudit, audit_id)


def get_audit_by_no(session: Session, audit_no: str) -> InternalAudit | None:
    return session.query(InternalAudit).filter(
        InternalAudit.audit_no == audit_no,
    ).first()


def create_audit(session: Session, data: dict) -> InternalAudit:
    obj = InternalAudit(**data)
    session.add(obj)
    session.flush()
    return obj


def update_audit(session: Session, audit_id: str, data: dict) -> InternalAudit | None:
    obj = session.get(InternalAudit, audit_id)
    if not obj:
        return None
    for k, v in data.items():
        if v is not None:
            setattr(obj, k, v)
    session.flush()
    return obj


def delete_audit(session: Session, audit_id: str) -> bool:
    obj = session.get(InternalAudit, audit_id)
    if not obj:
        return False
    session.delete(obj)
    session.flush()
    return True


# ── AuditFinding ───────────────────────────────────────

def list_findings(
    session: Session,
    *,
    audit_id: str | None = None,
    status: str | None = None,
    finding_type: str | None = None,
    requires_capa: bool | None = None,
    clause: str | None = None,
) -> list[AuditFinding]:
    q = session.query(AuditFinding)
    if audit_id:
        q = q.filter(AuditFinding.audit_id == audit_id)
    if status:
        q = q.filter(AuditFinding.status == status)
    if finding_type:
        q = q.filter(AuditFinding.finding_type == finding_type)
    if requires_capa is not None:
        q = q.filter(AuditFinding.requires_capa == requires_capa)
    if clause:
        q = q.filter(AuditFinding.clause == clause)
    return q.order_by(AuditFinding.finding_no.asc()).all()


def get_finding(session: Session, finding_id: str) -> AuditFinding | None:
    return session.get(AuditFinding, finding_id)


def get_finding_by_no(session: Session, finding_no: str) -> AuditFinding | None:
    return session.query(AuditFinding).filter(
        AuditFinding.finding_no == finding_no,
    ).first()


def create_finding(session: Session, data: dict) -> AuditFinding:
    obj = AuditFinding(**data)
    session.add(obj)
    session.flush()
    return obj


def update_finding(session: Session, finding_id: str, data: dict) -> AuditFinding | None:
    obj = session.get(AuditFinding, finding_id)
    if not obj:
        return None
    for k, v in data.items():
        if v is not None:
            setattr(obj, k, v)
    session.flush()
    return obj


def delete_finding(session: Session, finding_id: str) -> bool:
    obj = session.get(AuditFinding, finding_id)
    if not obj:
        return False
    session.delete(obj)
    session.flush()
    return True


def recompute_audit_counts(session: Session, audit_id: str) -> None:
    """重算稽核主檔的發現統計（總數、major/minor/observation）"""
    audit = session.get(InternalAudit, audit_id)
    if not audit:
        return
    findings = list_findings(session, audit_id=audit_id)
    audit.total_findings = len(findings)
    audit.major_findings_count = sum(
        1 for f in findings if f.finding_type == "major_nc"
    )
    audit.minor_findings_count = sum(
        1 for f in findings if f.finding_type == "minor_nc"
    )
    audit.observation_count = sum(
        1 for f in findings if f.finding_type == "observation"
    )
    session.flush()
