"""Service layer for Equipment / Calibration / Preventive Maintenance.

Implements ISO 9001:2015 §7.1.5 Monitoring and Measuring Resources:
- §7.1.5.1 設備適用性、維護
- §7.1.5.2 a) 對照可追溯至國家/國際標準
- §7.1.5.2 b) 識別校正狀態
- §7.1.5.2 c)-d) 失效時評估先前量測結果之有效性
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from dateutil.relativedelta import relativedelta

from sqlalchemy.orm import Session

from ..domain.transitions import validate_status_transition
from ..repositories import equipment as repo

VALID_EQUIPMENT_TYPES = {
    "measurement", "production", "utility", "tooling", "other",
}
VALID_EQUIPMENT_STATUSES = {"active", "hold", "repair", "retired"}
VALID_CALIBRATION_TYPES = {"internal", "external", "verification"}
VALID_CALIBRATION_RESULTS = {"passed", "failed", "conditional"}
VALID_CALIBRATION_STATUSES = {
    "planned", "in_progress", "completed", "verified", "cancelled",
}
VALID_PM_PLAN_TYPES = {
    "daily", "weekly", "monthly", "quarterly", "annual", "custom",
}
VALID_PM_TYPES = {
    "preventive", "corrective", "inspection", "calibration_support",
}
VALID_PM_RESULTS = {"ok", "minor_issue", "needs_repair", "failed"}
VALID_PM_STATUSES = {"planned", "in_progress", "completed", "cancelled"}


# ── Equipment ──────────────────────────────────────────

def list_equipments(session: Session, **filters) -> list[dict]:
    rows = repo.list_equipments(session, **filters)
    return [_equipment_to_dict(r) for r in rows]


def get_equipment(session: Session, equipment_id: str) -> dict | None:
    row = repo.get_equipment(session, equipment_id)
    return _equipment_to_dict(row) if row else None


def create_equipment(session: Session, data: dict) -> dict:
    if repo.get_equipment_by_no(session, data["equipment_no"]):
        raise ValueError(f"Equipment '{data['equipment_no']}' already exists")
    _validate_equipment_enums(data)
    _validate_calibration_settings(data)
    return _equipment_to_dict(repo.create_equipment(session, data))


def update_equipment(session: Session, equipment_id: str, data: dict) -> dict | None:
    current = repo.get_equipment(session, equipment_id)
    if not current:
        return None
    _validate_equipment_enums(data)
    # 合併當前值校驗校正設定一致性
    merged = {
        "requires_calibration": data.get(
            "requires_calibration", current.requires_calibration,
        ),
        "calibration_interval_months": data.get(
            "calibration_interval_months", current.calibration_interval_months,
        ),
        "requires_pm": data.get("requires_pm", current.requires_pm),
        "pm_interval_days": data.get("pm_interval_days", current.pm_interval_days),
    }
    _validate_calibration_settings(merged)
    # 狀態轉換檢查
    if "status" in data and data["status"] != current.status:
        err = validate_status_transition(
            "equipment", current.status, data["status"],
        )
        if err:
            raise ValueError(err)
    row = repo.update_equipment(session, equipment_id, data)
    return _equipment_to_dict(row) if row else None


def delete_equipment(session: Session, equipment_id: str) -> bool:
    return repo.delete_equipment(session, equipment_id)


# ── CalibrationRecord ──────────────────────────────────

def list_calibrations(session: Session, **filters) -> list[dict]:
    rows = repo.list_calibrations(session, **filters)
    return [_calibration_to_dict(r) for r in rows]


def get_calibration(session: Session, calibration_id: str) -> dict | None:
    row = repo.get_calibration(session, calibration_id)
    return _calibration_to_dict(row) if row else None


def create_calibration(session: Session, data: dict) -> dict:
    equipment = repo.get_equipment(session, data["equipment_id"])
    if not equipment:
        raise ValueError(f"Equipment '{data['equipment_id']}' not found")
    if repo.get_calibration_by_no(session, data["calibration_no"]):
        raise ValueError(
            f"Calibration '{data['calibration_no']}' already exists"
        )
    _validate_calibration_enums(data)
    row = repo.create_calibration(session, data)
    # 若建立時已為 verified 且已通過，立即同步到設備
    _sync_equipment_from_calibration(session, equipment, row)
    return _calibration_to_dict(row)


def update_calibration(
    session: Session, calibration_id: str, data: dict,
) -> dict | None:
    current = repo.get_calibration(session, calibration_id)
    if not current:
        return None
    _validate_calibration_enums(data)
    # 狀態轉換檢查
    if "status" in data and data["status"] != current.status:
        err = validate_status_transition(
            "calibration_record", current.status, data["status"],
        )
        if err:
            raise ValueError(err)
        # ISO §7.1.5.2 — verified 前必須有結果與 calibration_date
        if data["status"] == "verified":
            result = data.get("result") or current.result
            cal_date = data.get("calibration_date") or current.calibration_date
            if not result:
                raise ValueError(
                    "Cannot verify calibration: result must be set "
                    "(ISO 9001 §7.1.5.2)"
                )
            if not cal_date:
                raise ValueError(
                    "Cannot verify calibration: calibration_date required"
                )
            verified_by = data.get("verified_by") or current.verified_by
            if not verified_by:
                raise ValueError(
                    "Cannot verify calibration: verified_by must be set"
                )
            # 自動寫入 verified_at
            if not data.get("verified_at"):
                data["verified_at"] = datetime.now(timezone.utc)
    row = repo.update_calibration(session, calibration_id, data)
    if row:
        equipment = repo.get_equipment(session, row.equipment_id)
        if equipment:
            _sync_equipment_from_calibration(session, equipment, row)
    return _calibration_to_dict(row) if row else None


def delete_calibration(session: Session, calibration_id: str) -> bool:
    return repo.delete_calibration(session, calibration_id)


# ── EquipmentPMPlan ────────────────────────────────────

def list_pm_plans(session: Session, **filters) -> list[dict]:
    rows = repo.list_pm_plans(session, **filters)
    return [_pm_plan_to_dict(r) for r in rows]


def get_pm_plan(session: Session, plan_id: str) -> dict | None:
    row = repo.get_pm_plan(session, plan_id)
    return _pm_plan_to_dict(row) if row else None


def create_pm_plan(session: Session, data: dict) -> dict:
    if not repo.get_equipment(session, data["equipment_id"]):
        raise ValueError(f"Equipment '{data['equipment_id']}' not found")
    if repo.get_pm_plan_by_no(session, data["plan_no"]):
        raise ValueError(f"PM Plan '{data['plan_no']}' already exists")
    if data.get("plan_type") and data["plan_type"] not in VALID_PM_PLAN_TYPES:
        raise ValueError(
            f"Invalid plan_type. Allowed: {sorted(VALID_PM_PLAN_TYPES)}"
        )
    return _pm_plan_to_dict(repo.create_pm_plan(session, data))


def update_pm_plan(session: Session, plan_id: str, data: dict) -> dict | None:
    if not repo.get_pm_plan(session, plan_id):
        return None
    if "plan_type" in data and data["plan_type"] is not None:
        if data["plan_type"] not in VALID_PM_PLAN_TYPES:
            raise ValueError(
                f"Invalid plan_type. Allowed: {sorted(VALID_PM_PLAN_TYPES)}"
            )
    row = repo.update_pm_plan(session, plan_id, data)
    return _pm_plan_to_dict(row) if row else None


def delete_pm_plan(session: Session, plan_id: str) -> bool:
    return repo.delete_pm_plan(session, plan_id)


# ── EquipmentPMRecord ──────────────────────────────────

def list_pm_records(session: Session, **filters) -> list[dict]:
    rows = repo.list_pm_records(session, **filters)
    return [_pm_record_to_dict(r) for r in rows]


def get_pm_record(session: Session, pm_id: str) -> dict | None:
    row = repo.get_pm_record(session, pm_id)
    return _pm_record_to_dict(row) if row else None


def create_pm_record(session: Session, data: dict) -> dict:
    equipment = repo.get_equipment(session, data["equipment_id"])
    if not equipment:
        raise ValueError(f"Equipment '{data['equipment_id']}' not found")
    if equipment.status == "retired":
        raise ValueError(
            f"Cannot create PM record for retired equipment "
            f"'{equipment.equipment_no}'"
        )
    if repo.get_pm_record_by_no(session, data["pm_no"]):
        raise ValueError(f"PM record '{data['pm_no']}' already exists")
    if data.get("plan_id"):
        if not repo.get_pm_plan(session, data["plan_id"]):
            raise ValueError(f"PM plan '{data['plan_id']}' not found")
    _validate_pm_record_enums(data)
    row = repo.create_pm_record(session, data)
    _sync_equipment_from_pm(session, equipment, row)
    return _pm_record_to_dict(row)


def update_pm_record(session: Session, pm_id: str, data: dict) -> dict | None:
    current = repo.get_pm_record(session, pm_id)
    if not current:
        return None
    _validate_pm_record_enums(data)
    if data.get("plan_id"):
        if not repo.get_pm_plan(session, data["plan_id"]):
            raise ValueError(f"PM plan '{data['plan_id']}' not found")
    if "status" in data and data["status"] != current.status:
        err = validate_status_transition(
            "pm_record", current.status, data["status"],
        )
        if err:
            raise ValueError(err)
        if data["status"] == "completed":
            executed = data.get("executed_date") or current.executed_date
            performed_by = data.get("performed_by") or current.performed_by
            if not executed:
                raise ValueError(
                    "Cannot complete PM record: executed_date required"
                )
            if not performed_by:
                raise ValueError(
                    "Cannot complete PM record: performed_by required"
                )
    row = repo.update_pm_record(session, pm_id, data)
    if row:
        equipment = repo.get_equipment(session, row.equipment_id)
        if equipment:
            _sync_equipment_from_pm(session, equipment, row)
    return _pm_record_to_dict(row) if row else None


def delete_pm_record(session: Session, pm_id: str) -> bool:
    return repo.delete_pm_record(session, pm_id)


# ── helpers ────────────────────────────────────────────

def _validate_equipment_enums(data: dict) -> None:
    if "equipment_type" in data and data["equipment_type"] is not None:
        if data["equipment_type"] not in VALID_EQUIPMENT_TYPES:
            raise ValueError(
                f"Invalid equipment_type. Allowed: {sorted(VALID_EQUIPMENT_TYPES)}"
            )
    if "status" in data and data["status"] is not None:
        if data["status"] not in VALID_EQUIPMENT_STATUSES:
            raise ValueError(
                f"Invalid status. Allowed: {sorted(VALID_EQUIPMENT_STATUSES)}"
            )


def _validate_calibration_settings(data: dict) -> None:
    """ISO §7.1.5.2 — 需校正設備必須有週期"""
    if data.get("requires_calibration"):
        if not data.get("calibration_interval_months"):
            raise ValueError(
                "calibration_interval_months must be > 0 when "
                "requires_calibration is True (ISO 9001 §7.1.5.2)"
            )
    if data.get("requires_pm"):
        if not data.get("pm_interval_days"):
            raise ValueError(
                "pm_interval_days must be > 0 when requires_pm is True"
            )


def _validate_calibration_enums(data: dict) -> None:
    if "calibration_type" in data and data["calibration_type"] is not None:
        if data["calibration_type"] not in VALID_CALIBRATION_TYPES:
            raise ValueError(
                f"Invalid calibration_type. Allowed: {sorted(VALID_CALIBRATION_TYPES)}"
            )
    if "result" in data and data["result"]:
        if data["result"] not in VALID_CALIBRATION_RESULTS:
            raise ValueError(
                f"Invalid result. Allowed: {sorted(VALID_CALIBRATION_RESULTS)}"
            )
    if "status" in data and data["status"] is not None:
        if data["status"] not in VALID_CALIBRATION_STATUSES:
            raise ValueError(
                f"Invalid status. Allowed: {sorted(VALID_CALIBRATION_STATUSES)}"
            )


def _validate_pm_record_enums(data: dict) -> None:
    if "pm_type" in data and data["pm_type"] is not None:
        if data["pm_type"] not in VALID_PM_TYPES:
            raise ValueError(
                f"Invalid pm_type. Allowed: {sorted(VALID_PM_TYPES)}"
            )
    if "result" in data and data["result"]:
        if data["result"] not in VALID_PM_RESULTS:
            raise ValueError(
                f"Invalid result. Allowed: {sorted(VALID_PM_RESULTS)}"
            )
    if "status" in data and data["status"] is not None:
        if data["status"] not in VALID_PM_STATUSES:
            raise ValueError(
                f"Invalid status. Allowed: {sorted(VALID_PM_STATUSES)}"
            )


def _sync_equipment_from_calibration(
    session: Session, equipment, calibration,
) -> None:
    """ISO §7.1.5.2 同步校正結果到設備主檔。

    - verified 且 result=passed → 更新 last_calibration_date, next_calibration_due
    - verified 且 result=failed → 設備轉 hold
    """
    if calibration.status != "verified":
        return
    changes: dict = {}
    if calibration.result == "passed":
        cal_date: date | None = calibration.calibration_date
        if cal_date:
            changes["last_calibration_date"] = cal_date
            if equipment.calibration_interval_months > 0:
                changes["next_calibration_due"] = (
                    calibration.next_due_date
                    or cal_date + relativedelta(
                        months=equipment.calibration_interval_months,
                    )
                )
    elif calibration.result == "failed":
        # ISO §7.1.5.2 b) — 失效量具應識別狀態並隔離
        if equipment.status == "active":
            changes["status"] = "hold"
            changes["hold_reason"] = (
                f"Calibration {calibration.calibration_no} failed — "
                f"pending impact assessment (ISO 9001 §7.1.5.2 c)"
            )
    if changes:
        repo.update_equipment(session, equipment.id, changes)


def _sync_equipment_from_pm(
    session: Session, equipment, pm_record,
) -> None:
    """PM 完成時同步到設備主檔的 last_pm_date / next_pm_due"""
    if pm_record.status != "completed":
        return
    changes: dict = {}
    executed = pm_record.executed_date
    if executed:
        changes["last_pm_date"] = executed
        if equipment.pm_interval_days > 0:
            changes["next_pm_due"] = (
                pm_record.next_due_date
                or executed + relativedelta(days=equipment.pm_interval_days)
            )
    # needs_repair 或 failed → 設備轉 repair
    if pm_record.result in {"needs_repair", "failed"}:
        if equipment.status == "active":
            changes["status"] = "repair"
            changes["hold_reason"] = (
                f"PM {pm_record.pm_no} flagged {pm_record.result}"
            )
    if changes:
        repo.update_equipment(session, equipment.id, changes)


def _equipment_to_dict(row) -> dict:
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}


def _calibration_to_dict(row) -> dict:
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}


def _pm_plan_to_dict(row) -> dict:
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}


def _pm_record_to_dict(row) -> dict:
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}
