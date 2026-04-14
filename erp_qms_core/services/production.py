from __future__ import annotations

from sqlalchemy.orm import Session

from ..domain.transitions import validate_status_transition
from ..repositories import production as repo


# ── ProductionPlan ──────────────────────────────────────

def list_production_plans(session: Session, status: str | None = None, work_order_id: str | None = None) -> list[dict]:
    rows = repo.list_production_plans(session, status=status, work_order_id=work_order_id)
    return [_row_to_dict(r) for r in rows]


def get_production_plan(session: Session, plan_id: str) -> dict | None:
    row = repo.get_production_plan(session, plan_id)
    return _row_to_dict(row) if row else None


def create_production_plan(session: Session, data: dict) -> dict:
    if repo.get_production_plan_by_no(session, data["plan_no"]):
        raise ValueError(f"Production plan '{data['plan_no']}' already exists")
    return _row_to_dict(repo.create_production_plan(session, data))


def update_production_plan(session: Session, plan_id: str, data: dict) -> dict | None:
    if "status" in data and data["status"] is not None:
        existing = repo.get_production_plan(session, plan_id)
        if not existing:
            return None
        err = validate_status_transition("production_plan", existing.status, data["status"])
        if err:
            raise ValueError(err)
    row = repo.update_production_plan(session, plan_id, data)
    return _row_to_dict(row) if row else None


def delete_production_plan(session: Session, plan_id: str) -> bool:
    return repo.delete_production_plan(session, plan_id)


# ── MaterialIssue ───────────────────────────────────────

def list_material_issues(session: Session, status: str | None = None, work_order_id: str | None = None) -> list[dict]:
    rows = repo.list_material_issues(session, status=status, work_order_id=work_order_id)
    return [_mi_to_dict(r) for r in rows]


def get_material_issue(session: Session, issue_id: str) -> dict | None:
    row = repo.get_material_issue(session, issue_id)
    return _mi_to_dict(row) if row else None


def create_material_issue(session: Session, data: dict) -> dict:
    if repo.get_material_issue_by_no(session, data["issue_no"]):
        raise ValueError(f"Material issue '{data['issue_no']}' already exists")
    items = data.pop("items", [])
    return _mi_to_dict(repo.create_material_issue(session, data, items=items))


def update_material_issue(session: Session, issue_id: str, data: dict) -> dict | None:
    if "status" in data and data["status"] is not None:
        existing = repo.get_material_issue(session, issue_id)
        if not existing:
            return None
        err = validate_status_transition("material_issue", existing.status, data["status"])
        if err:
            raise ValueError(err)
    items = data.pop("items", None)
    row = repo.update_material_issue(session, issue_id, data, items=items)
    return _mi_to_dict(row) if row else None


def delete_material_issue(session: Session, issue_id: str) -> bool:
    return repo.delete_material_issue(session, issue_id)


# ── helpers ─────────────────────────────────────────────

def _row_to_dict(row) -> dict:
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}


def _mi_to_dict(issue) -> dict:
    d = _row_to_dict(issue)
    d["items"] = [_row_to_dict(i) for i in issue.items]
    return d
