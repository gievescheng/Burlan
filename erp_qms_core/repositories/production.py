from __future__ import annotations

from sqlalchemy.orm import Session

from ..models.production import MaterialIssue, MaterialIssueItem, ProductionPlan


# ── ProductionPlan ──────────────────────────────────────

def list_production_plans(
    session: Session,
    *,
    status: str | None = None,
    work_order_id: str | None = None,
) -> list[ProductionPlan]:
    q = session.query(ProductionPlan)
    if status:
        q = q.filter(ProductionPlan.status == status)
    if work_order_id:
        q = q.filter(ProductionPlan.work_order_id == work_order_id)
    return q.order_by(ProductionPlan.plan_no.desc()).all()


def get_production_plan(session: Session, plan_id: str) -> ProductionPlan | None:
    return session.get(ProductionPlan, plan_id)


def get_production_plan_by_no(session: Session, plan_no: str) -> ProductionPlan | None:
    return session.query(ProductionPlan).filter(ProductionPlan.plan_no == plan_no).first()


def create_production_plan(session: Session, data: dict) -> ProductionPlan:
    obj = ProductionPlan(**data)
    session.add(obj)
    session.flush()
    return obj


def update_production_plan(session: Session, plan_id: str, data: dict) -> ProductionPlan | None:
    obj = session.get(ProductionPlan, plan_id)
    if not obj:
        return None
    for k, v in data.items():
        if v is not None:
            setattr(obj, k, v)
    session.flush()
    return obj


def delete_production_plan(session: Session, plan_id: str) -> bool:
    obj = session.get(ProductionPlan, plan_id)
    if not obj:
        return False
    session.delete(obj)
    session.flush()
    return True


# ── MaterialIssue ───────────────────────────────────────

def list_material_issues(
    session: Session,
    *,
    status: str | None = None,
    work_order_id: str | None = None,
) -> list[MaterialIssue]:
    q = session.query(MaterialIssue)
    if status:
        q = q.filter(MaterialIssue.status == status)
    if work_order_id:
        q = q.filter(MaterialIssue.work_order_id == work_order_id)
    return q.order_by(MaterialIssue.issue_no.desc()).all()


def get_material_issue(session: Session, issue_id: str) -> MaterialIssue | None:
    return session.get(MaterialIssue, issue_id)


def get_material_issue_by_no(session: Session, issue_no: str) -> MaterialIssue | None:
    return session.query(MaterialIssue).filter(MaterialIssue.issue_no == issue_no).first()


def create_material_issue(session: Session, data: dict, items: list[dict] | None = None) -> MaterialIssue:
    issue = MaterialIssue(**data)
    session.add(issue)
    session.flush()
    if items:
        for item_data in items:
            item = MaterialIssueItem(issue_id=issue.id, **item_data)
            session.add(item)
        session.flush()
    return issue


def update_material_issue(
    session: Session, issue_id: str, data: dict, items: list[dict] | None = None,
) -> MaterialIssue | None:
    issue = session.get(MaterialIssue, issue_id)
    if not issue:
        return None
    for k, v in data.items():
        if v is not None:
            setattr(issue, k, v)
    if items is not None:
        for old in list(issue.items):
            session.delete(old)
        session.flush()
        for item_data in items:
            item = MaterialIssueItem(issue_id=issue.id, **item_data)
            session.add(item)
        session.flush()
        session.expire(issue, ["items"])
    session.flush()
    return issue


def delete_material_issue(session: Session, issue_id: str) -> bool:
    issue = session.get(MaterialIssue, issue_id)
    if not issue:
        return False
    session.delete(issue)
    session.flush()
    return True
