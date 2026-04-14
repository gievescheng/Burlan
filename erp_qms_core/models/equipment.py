"""Equipment, Calibration, and Preventive Maintenance (ISO 9001:2015 §7.1.5).

§7.1.5.1 General — 監視與量測資源之提供
§7.1.5.2 Measurement traceability — 可追溯性、校正、識別狀態
"""
from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .base import AuditMixin, new_id


class Equipment(AuditMixin, Base):
    """設備 / 量測儀器主檔 — ISO §7.1.5.1"""
    __tablename__ = "erp_equipments"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=new_id)
    equipment_no: Mapped[str] = mapped_column(Text, unique=True, index=True)
    name: Mapped[str] = mapped_column(Text, default="")
    # 設備類型
    equipment_type: Mapped[str] = mapped_column(Text, default="measurement", index=True)
    # measurement / production / utility / tooling / other
    category: Mapped[str] = mapped_column(Text, default="", index=True)
    model: Mapped[str] = mapped_column(Text, default="")
    manufacturer: Mapped[str] = mapped_column(Text, default="")
    serial_no: Mapped[str] = mapped_column(Text, default="", index=True)
    # 位置 / 擁有部門
    location: Mapped[str] = mapped_column(Text, default="")
    department: Mapped[str] = mapped_column(Text, default="", index=True)
    responsible_person: Mapped[str] = mapped_column(Text, default="")
    acquired_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # ── 校正管理（§7.1.5.2） ─────────────────
    requires_calibration: Mapped[bool] = mapped_column(
        Boolean, default=False, index=True,
    )
    calibration_interval_months: Mapped[int] = mapped_column(Integer, default=0)
    last_calibration_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    next_calibration_due: Mapped[date | None] = mapped_column(
        Date, nullable=True, index=True,
    )

    # ── 預防保養管理 ─────────────────────────
    requires_pm: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    pm_interval_days: Mapped[int] = mapped_column(Integer, default=0)
    last_pm_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    next_pm_due: Mapped[date | None] = mapped_column(
        Date, nullable=True, index=True,
    )

    # 狀態 — ISO §7.1.5.2 b) 保存識別狀態
    status: Mapped[str] = mapped_column(Text, default="active", index=True)
    # active / hold / repair / retired
    hold_reason: Mapped[str] = mapped_column(Text, default="")
    notes: Mapped[str] = mapped_column(Text, default="")

    calibrations: Mapped[list[CalibrationRecord]] = relationship(
        back_populates="equipment",
        cascade="all, delete-orphan",
        order_by="CalibrationRecord.calibration_date.desc()",
    )
    pm_records: Mapped[list[EquipmentPMRecord]] = relationship(
        back_populates="equipment",
        cascade="all, delete-orphan",
        order_by="EquipmentPMRecord.scheduled_date.desc()",
    )


class CalibrationRecord(AuditMixin, Base):
    """校正紀錄 — ISO §7.1.5.2 a)-d) 量測可追溯性與失效處置"""
    __tablename__ = "erp_calibration_records"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=new_id)
    calibration_no: Mapped[str] = mapped_column(Text, unique=True, index=True)
    equipment_id: Mapped[str] = mapped_column(
        ForeignKey("erp_equipments.id", ondelete="CASCADE"), index=True,
    )
    # 校正類型
    calibration_type: Mapped[str] = mapped_column(
        Text, default="external", index=True,
    )
    # internal / external / verification
    calibration_date: Mapped[date | None] = mapped_column(
        Date, nullable=True, index=True,
    )
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    next_due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    # 執行者 / 廠商 / 證書
    calibrator: Mapped[str] = mapped_column(Text, default="")
    vendor: Mapped[str] = mapped_column(Text, default="")
    certificate_no: Mapped[str] = mapped_column(Text, default="", index=True)
    standard_used: Mapped[str] = mapped_column(Text, default="")
    # 量測結果
    reading_before: Mapped[float | None] = mapped_column(Float, nullable=True)
    reading_after: Mapped[float | None] = mapped_column(Float, nullable=True)
    deviation: Mapped[float | None] = mapped_column(Float, nullable=True)
    tolerance: Mapped[float | None] = mapped_column(Float, nullable=True)
    adjustment_made: Mapped[bool] = mapped_column(Boolean, default=False)
    result: Mapped[str] = mapped_column(Text, default="", index=True)
    # passed / failed / conditional
    # ISO §7.1.5.2 c)-d) — 失效時之衝擊評估
    affected_lots: Mapped[str] = mapped_column(Text, default="")
    impact_assessment: Mapped[str] = mapped_column(Text, default="")
    # 工作流程
    status: Mapped[str] = mapped_column(Text, default="planned", index=True)
    # planned / in_progress / completed / verified / cancelled
    verified_by: Mapped[str] = mapped_column(Text, default="")
    verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    notes: Mapped[str] = mapped_column(Text, default="")

    equipment: Mapped[Equipment] = relationship(back_populates="calibrations")


class EquipmentPMPlan(AuditMixin, Base):
    """預防保養計畫"""
    __tablename__ = "erp_equipment_pm_plans"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=new_id)
    plan_no: Mapped[str] = mapped_column(Text, unique=True, index=True)
    equipment_id: Mapped[str] = mapped_column(
        ForeignKey("erp_equipments.id", ondelete="CASCADE"), index=True,
    )
    title: Mapped[str] = mapped_column(Text, default="")
    plan_type: Mapped[str] = mapped_column(Text, default="monthly", index=True)
    # daily / weekly / monthly / quarterly / annual / custom
    interval_days: Mapped[int] = mapped_column(Integer, default=30)
    tasks: Mapped[str] = mapped_column(Text, default="")
    responsible_dept: Mapped[str] = mapped_column(Text, default="")
    responsible_person: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(Text, default="active", index=True)
    # active / inactive
    notes: Mapped[str] = mapped_column(Text, default="")


class EquipmentPMRecord(AuditMixin, Base):
    """預防保養 / 維修執行紀錄"""
    __tablename__ = "erp_equipment_pm_records"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=new_id)
    pm_no: Mapped[str] = mapped_column(Text, unique=True, index=True)
    equipment_id: Mapped[str] = mapped_column(
        ForeignKey("erp_equipments.id", ondelete="CASCADE"), index=True,
    )
    plan_id: Mapped[str | None] = mapped_column(
        ForeignKey("erp_equipment_pm_plans.id"), nullable=True, index=True,
    )
    pm_type: Mapped[str] = mapped_column(Text, default="preventive", index=True)
    # preventive / corrective / inspection / calibration_support
    scheduled_date: Mapped[date | None] = mapped_column(
        Date, nullable=True, index=True,
    )
    executed_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    performed_by: Mapped[str] = mapped_column(Text, default="")
    supervisor: Mapped[str] = mapped_column(Text, default="")
    tasks_performed: Mapped[str] = mapped_column(Text, default="")
    result: Mapped[str] = mapped_column(Text, default="", index=True)
    # ok / minor_issue / needs_repair / failed
    findings: Mapped[str] = mapped_column(Text, default="")
    parts_replaced: Mapped[str] = mapped_column(Text, default="")
    downtime_hours: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(Text, default="planned", index=True)
    # planned / in_progress / completed / cancelled
    next_due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")

    equipment: Mapped[Equipment] = relationship(back_populates="pm_records")
