from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .. import database
from ..schemas.production import (
    MaterialIssueCreate, MaterialIssueOut, MaterialIssueUpdate,
    ProductionPlanCreate, ProductionPlanOut, ProductionPlanUpdate,
)
from ..services import production as svc

router = APIRouter()


# ── ProductionPlan ──────────────────────────────────────

@router.get("/production-plans", response_model=list[ProductionPlanOut])
def list_production_plans(status: str | None = None, work_order_id: str | None = None):
    with database.session_scope() as s:
        return svc.list_production_plans(s, status=status, work_order_id=work_order_id)


@router.get("/production-plans/{plan_id}", response_model=ProductionPlanOut)
def get_production_plan(plan_id: str):
    with database.session_scope() as s:
        row = svc.get_production_plan(s, plan_id)
    if not row:
        raise HTTPException(404, "Production plan not found")
    return row


@router.post("/production-plans", response_model=ProductionPlanOut, status_code=201)
def create_production_plan(body: ProductionPlanCreate):
    try:
        with database.session_scope() as s:
            return svc.create_production_plan(s, body.model_dump())
    except ValueError as e:
        raise HTTPException(409, str(e))


@router.patch("/production-plans/{plan_id}", response_model=ProductionPlanOut)
def update_production_plan(plan_id: str, body: ProductionPlanUpdate):
    try:
        with database.session_scope() as s:
            row = svc.update_production_plan(s, plan_id, body.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(422, str(e))
    if not row:
        raise HTTPException(404, "Production plan not found")
    return row


@router.delete("/production-plans/{plan_id}", status_code=204)
def delete_production_plan(plan_id: str):
    with database.session_scope() as s:
        if not svc.delete_production_plan(s, plan_id):
            raise HTTPException(404, "Production plan not found")


# ── MaterialIssue ───────────────────────────────────────

@router.get("/material-issues", response_model=list[MaterialIssueOut])
def list_material_issues(status: str | None = None, work_order_id: str | None = None):
    with database.session_scope() as s:
        return svc.list_material_issues(s, status=status, work_order_id=work_order_id)


@router.get("/material-issues/{issue_id}", response_model=MaterialIssueOut)
def get_material_issue(issue_id: str):
    with database.session_scope() as s:
        row = svc.get_material_issue(s, issue_id)
    if not row:
        raise HTTPException(404, "Material issue not found")
    return row


@router.post("/material-issues", response_model=MaterialIssueOut, status_code=201)
def create_material_issue(body: MaterialIssueCreate):
    try:
        with database.session_scope() as s:
            return svc.create_material_issue(s, body.model_dump())
    except ValueError as e:
        raise HTTPException(409, str(e))


@router.patch("/material-issues/{issue_id}", response_model=MaterialIssueOut)
def update_material_issue(issue_id: str, body: MaterialIssueUpdate):
    try:
        with database.session_scope() as s:
            row = svc.update_material_issue(s, issue_id, body.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(422, str(e))
    if not row:
        raise HTTPException(404, "Material issue not found")
    return row


@router.delete("/material-issues/{issue_id}", status_code=204)
def delete_material_issue(issue_id: str):
    with database.session_scope() as s:
        if not svc.delete_material_issue(s, issue_id):
            raise HTTPException(404, "Material issue not found")
