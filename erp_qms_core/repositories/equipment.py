from __future__ import annotations

from sqlalchemy.orm import Session

from ..models.equipment import (
    Equipment, CalibrationRecord, EquipmentPMPlan, EquipmentPMRecord,
)


# ── Equipment ──────────────────────────────────────────

def list_equipments(
    session: Session,
    *,
    status: str | None = None,
    equipment_type: str | None = None,
    department: str | None = None,
    requires_calibration: bool | None = None,
    requires_pm: bool | None = None,
) -> list[Equipment]:
    q = session.query(Equipment)
    if status:
        q = q.filter(Equipment.status == status)
    if equipment_type:
        q = q.filter(Equipment.equipment_type == equipment_type)
    if department:
        q = q.filter(Equipment.department == department)
    if requires_calibration is not None:
        q = q.filter(Equipment.requires_calibration == requires_calibration)
    if requires_pm is not None:
        q = q.filter(Equipment.requires_pm == requires_pm)
    return q.order_by(Equipment.equipment_no.asc()).all()


def get_equipment(session: Session, equipment_id: str) -> Equipment | None:
    return session.get(Equipment, equipment_id)


def get_equipment_by_no(session: Session, equipment_no: str) -> Equipment | None:
    return session.query(Equipment).filter(
        Equipment.equipment_no == equipment_no,
    ).first()


def create_equipment(session: Session, data: dict) -> Equipment:
    obj = Equipment(**data)
    session.add(obj)
    session.flush()
    return obj


def update_equipment(session: Session, equipment_id: str, data: dict) -> Equipment | None:
    obj = session.get(Equipment, equipment_id)
    if not obj:
        return None
    for k, v in data.items():
        if v is not None:
            setattr(obj, k, v)
    session.flush()
    return obj


def delete_equipment(session: Session, equipment_id: str) -> bool:
    obj = session.get(Equipment, equipment_id)
    if not obj:
        return False
    session.delete(obj)
    session.flush()
    return True


# ── CalibrationRecord ──────────────────────────────────

def list_calibrations(
    session: Session,
    *,
    equipment_id: str | None = None,
    status: str | None = None,
    result: str | None = None,
    calibration_type: str | None = None,
) -> list[CalibrationRecord]:
    q = session.query(CalibrationRecord)
    if equipment_id:
        q = q.filter(CalibrationRecord.equipment_id == equipment_id)
    if status:
        q = q.filter(CalibrationRecord.status == status)
    if result:
        q = q.filter(CalibrationRecord.result == result)
    if calibration_type:
        q = q.filter(CalibrationRecord.calibration_type == calibration_type)
    return q.order_by(CalibrationRecord.calibration_no.desc()).all()


def get_calibration(session: Session, calibration_id: str) -> CalibrationRecord | None:
    return session.get(CalibrationRecord, calibration_id)


def get_calibration_by_no(session: Session, calibration_no: str) -> CalibrationRecord | None:
    return session.query(CalibrationRecord).filter(
        CalibrationRecord.calibration_no == calibration_no,
    ).first()


def create_calibration(session: Session, data: dict) -> CalibrationRecord:
    obj = CalibrationRecord(**data)
    session.add(obj)
    session.flush()
    return obj


def update_calibration(session: Session, calibration_id: str, data: dict) -> CalibrationRecord | None:
    obj = session.get(CalibrationRecord, calibration_id)
    if not obj:
        return None
    for k, v in data.items():
        if v is not None:
            setattr(obj, k, v)
    session.flush()
    return obj


def delete_calibration(session: Session, calibration_id: str) -> bool:
    obj = session.get(CalibrationRecord, calibration_id)
    if not obj:
        return False
    session.delete(obj)
    session.flush()
    return True


# ── EquipmentPMPlan ────────────────────────────────────

def list_pm_plans(
    session: Session,
    *,
    equipment_id: str | None = None,
    status: str | None = None,
    plan_type: str | None = None,
) -> list[EquipmentPMPlan]:
    q = session.query(EquipmentPMPlan)
    if equipment_id:
        q = q.filter(EquipmentPMPlan.equipment_id == equipment_id)
    if status:
        q = q.filter(EquipmentPMPlan.status == status)
    if plan_type:
        q = q.filter(EquipmentPMPlan.plan_type == plan_type)
    return q.order_by(EquipmentPMPlan.plan_no.asc()).all()


def get_pm_plan(session: Session, plan_id: str) -> EquipmentPMPlan | None:
    return session.get(EquipmentPMPlan, plan_id)


def get_pm_plan_by_no(session: Session, plan_no: str) -> EquipmentPMPlan | None:
    return session.query(EquipmentPMPlan).filter(
        EquipmentPMPlan.plan_no == plan_no,
    ).first()


def create_pm_plan(session: Session, data: dict) -> EquipmentPMPlan:
    obj = EquipmentPMPlan(**data)
    session.add(obj)
    session.flush()
    return obj


def update_pm_plan(session: Session, plan_id: str, data: dict) -> EquipmentPMPlan | None:
    obj = session.get(EquipmentPMPlan, plan_id)
    if not obj:
        return None
    for k, v in data.items():
        if v is not None:
            setattr(obj, k, v)
    session.flush()
    return obj


def delete_pm_plan(session: Session, plan_id: str) -> bool:
    obj = session.get(EquipmentPMPlan, plan_id)
    if not obj:
        return False
    session.delete(obj)
    session.flush()
    return True


# ── EquipmentPMRecord ──────────────────────────────────

def list_pm_records(
    session: Session,
    *,
    equipment_id: str | None = None,
    plan_id: str | None = None,
    status: str | None = None,
    pm_type: str | None = None,
    result: str | None = None,
) -> list[EquipmentPMRecord]:
    q = session.query(EquipmentPMRecord)
    if equipment_id:
        q = q.filter(EquipmentPMRecord.equipment_id == equipment_id)
    if plan_id:
        q = q.filter(EquipmentPMRecord.plan_id == plan_id)
    if status:
        q = q.filter(EquipmentPMRecord.status == status)
    if pm_type:
        q = q.filter(EquipmentPMRecord.pm_type == pm_type)
    if result:
        q = q.filter(EquipmentPMRecord.result == result)
    return q.order_by(EquipmentPMRecord.pm_no.desc()).all()


def get_pm_record(session: Session, pm_id: str) -> EquipmentPMRecord | None:
    return session.get(EquipmentPMRecord, pm_id)


def get_pm_record_by_no(session: Session, pm_no: str) -> EquipmentPMRecord | None:
    return session.query(EquipmentPMRecord).filter(
        EquipmentPMRecord.pm_no == pm_no,
    ).first()


def create_pm_record(session: Session, data: dict) -> EquipmentPMRecord:
    obj = EquipmentPMRecord(**data)
    session.add(obj)
    session.flush()
    return obj


def update_pm_record(session: Session, pm_id: str, data: dict) -> EquipmentPMRecord | None:
    obj = session.get(EquipmentPMRecord, pm_id)
    if not obj:
        return None
    for k, v in data.items():
        if v is not None:
            setattr(obj, k, v)
    session.flush()
    return obj


def delete_pm_record(session: Session, pm_id: str) -> bool:
    obj = session.get(EquipmentPMRecord, pm_id)
    if not obj:
        return False
    session.delete(obj)
    session.flush()
    return True
