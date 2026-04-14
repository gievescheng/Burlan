from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .. import database
from ..schemas.equipment import (
    EquipmentCreate, EquipmentOut, EquipmentUpdate,
    CalibrationCreate, CalibrationOut, CalibrationUpdate,
    PMPlanCreate, PMPlanOut, PMPlanUpdate,
    PMRecordCreate, PMRecordOut, PMRecordUpdate,
)
from ..services import equipment as svc

router = APIRouter()


# ── Equipment ──────────────────────────────────────────

@router.get("/equipments", response_model=list[EquipmentOut])
def list_equipments(
    status: str | None = None,
    equipment_type: str | None = None,
    department: str | None = None,
    requires_calibration: bool | None = None,
    requires_pm: bool | None = None,
):
    with database.session_scope() as s:
        return svc.list_equipments(
            s, status=status, equipment_type=equipment_type,
            department=department,
            requires_calibration=requires_calibration,
            requires_pm=requires_pm,
        )


@router.get("/equipments/{equipment_id}", response_model=EquipmentOut)
def get_equipment(equipment_id: str):
    with database.session_scope() as s:
        row = svc.get_equipment(s, equipment_id)
    if not row:
        raise HTTPException(404, "Equipment not found")
    return row


@router.post("/equipments", response_model=EquipmentOut, status_code=201)
def create_equipment(body: EquipmentCreate):
    try:
        with database.session_scope() as s:
            return svc.create_equipment(s, body.model_dump())
    except ValueError as e:
        msg = str(e)
        if "already exists" in msg:
            raise HTTPException(409, msg)
        raise HTTPException(422, msg)


@router.patch("/equipments/{equipment_id}", response_model=EquipmentOut)
def update_equipment(equipment_id: str, body: EquipmentUpdate):
    try:
        with database.session_scope() as s:
            row = svc.update_equipment(s, equipment_id, body.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(422, str(e))
    if not row:
        raise HTTPException(404, "Equipment not found")
    return row


@router.delete("/equipments/{equipment_id}", status_code=204)
def delete_equipment(equipment_id: str):
    with database.session_scope() as s:
        if not svc.delete_equipment(s, equipment_id):
            raise HTTPException(404, "Equipment not found")


# ── CalibrationRecord ──────────────────────────────────

@router.get("/calibrations", response_model=list[CalibrationOut])
def list_calibrations(
    equipment_id: str | None = None,
    status: str | None = None,
    result: str | None = None,
    calibration_type: str | None = None,
):
    with database.session_scope() as s:
        return svc.list_calibrations(
            s, equipment_id=equipment_id, status=status,
            result=result, calibration_type=calibration_type,
        )


@router.get("/calibrations/{calibration_id}", response_model=CalibrationOut)
def get_calibration(calibration_id: str):
    with database.session_scope() as s:
        row = svc.get_calibration(s, calibration_id)
    if not row:
        raise HTTPException(404, "Calibration not found")
    return row


@router.post("/calibrations", response_model=CalibrationOut, status_code=201)
def create_calibration(body: CalibrationCreate):
    try:
        with database.session_scope() as s:
            return svc.create_calibration(s, body.model_dump())
    except ValueError as e:
        msg = str(e)
        if "already exists" in msg:
            raise HTTPException(409, msg)
        raise HTTPException(422, msg)


@router.patch("/calibrations/{calibration_id}", response_model=CalibrationOut)
def update_calibration(calibration_id: str, body: CalibrationUpdate):
    try:
        with database.session_scope() as s:
            row = svc.update_calibration(s, calibration_id, body.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(422, str(e))
    if not row:
        raise HTTPException(404, "Calibration not found")
    return row


@router.delete("/calibrations/{calibration_id}", status_code=204)
def delete_calibration(calibration_id: str):
    with database.session_scope() as s:
        if not svc.delete_calibration(s, calibration_id):
            raise HTTPException(404, "Calibration not found")


# ── EquipmentPMPlan ────────────────────────────────────

@router.get("/pm-plans", response_model=list[PMPlanOut])
def list_pm_plans(
    equipment_id: str | None = None,
    status: str | None = None,
    plan_type: str | None = None,
):
    with database.session_scope() as s:
        return svc.list_pm_plans(
            s, equipment_id=equipment_id, status=status, plan_type=plan_type,
        )


@router.get("/pm-plans/{plan_id}", response_model=PMPlanOut)
def get_pm_plan(plan_id: str):
    with database.session_scope() as s:
        row = svc.get_pm_plan(s, plan_id)
    if not row:
        raise HTTPException(404, "PM plan not found")
    return row


@router.post("/pm-plans", response_model=PMPlanOut, status_code=201)
def create_pm_plan(body: PMPlanCreate):
    try:
        with database.session_scope() as s:
            return svc.create_pm_plan(s, body.model_dump())
    except ValueError as e:
        msg = str(e)
        if "already exists" in msg:
            raise HTTPException(409, msg)
        raise HTTPException(422, msg)


@router.patch("/pm-plans/{plan_id}", response_model=PMPlanOut)
def update_pm_plan(plan_id: str, body: PMPlanUpdate):
    try:
        with database.session_scope() as s:
            row = svc.update_pm_plan(s, plan_id, body.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(422, str(e))
    if not row:
        raise HTTPException(404, "PM plan not found")
    return row


@router.delete("/pm-plans/{plan_id}", status_code=204)
def delete_pm_plan(plan_id: str):
    with database.session_scope() as s:
        if not svc.delete_pm_plan(s, plan_id):
            raise HTTPException(404, "PM plan not found")


# ── EquipmentPMRecord ──────────────────────────────────

@router.get("/pm-records", response_model=list[PMRecordOut])
def list_pm_records(
    equipment_id: str | None = None,
    plan_id: str | None = None,
    status: str | None = None,
    pm_type: str | None = None,
    result: str | None = None,
):
    with database.session_scope() as s:
        return svc.list_pm_records(
            s, equipment_id=equipment_id, plan_id=plan_id,
            status=status, pm_type=pm_type, result=result,
        )


@router.get("/pm-records/{pm_id}", response_model=PMRecordOut)
def get_pm_record(pm_id: str):
    with database.session_scope() as s:
        row = svc.get_pm_record(s, pm_id)
    if not row:
        raise HTTPException(404, "PM record not found")
    return row


@router.post("/pm-records", response_model=PMRecordOut, status_code=201)
def create_pm_record(body: PMRecordCreate):
    try:
        with database.session_scope() as s:
            return svc.create_pm_record(s, body.model_dump())
    except ValueError as e:
        msg = str(e)
        if "already exists" in msg:
            raise HTTPException(409, msg)
        raise HTTPException(422, msg)


@router.patch("/pm-records/{pm_id}", response_model=PMRecordOut)
def update_pm_record(pm_id: str, body: PMRecordUpdate):
    try:
        with database.session_scope() as s:
            row = svc.update_pm_record(s, pm_id, body.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(422, str(e))
    if not row:
        raise HTTPException(404, "PM record not found")
    return row


@router.delete("/pm-records/{pm_id}", status_code=204)
def delete_pm_record(pm_id: str):
    with database.session_scope() as s:
        if not svc.delete_pm_record(s, pm_id):
            raise HTTPException(404, "PM record not found")
