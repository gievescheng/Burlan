from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .base import AuditMixin, new_id, utcnow


class ProductionLog(AuditMixin, Base):
    """生產日誌 — 記錄每站每班生產實績"""
    __tablename__ = "erp_production_logs"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=new_id)
    log_no: Mapped[str] = mapped_column(Text, unique=True, index=True)
    work_order_id: Mapped[str] = mapped_column(
        ForeignKey("erp_work_orders.id"), index=True,
    )
    production_plan_id: Mapped[str | None] = mapped_column(
        ForeignKey("erp_production_plans.id"), index=True, nullable=True,
    )
    station_id: Mapped[str | None] = mapped_column(
        ForeignKey("erp_process_stations.id"), index=True, nullable=True,
    )
    product_id: Mapped[str] = mapped_column(
        ForeignKey("erp_products.id"), index=True,
    )
    # 追蹤
    lot_no: Mapped[str] = mapped_column(Text, default="", index=True)
    wafer_lot: Mapped[str] = mapped_column(Text, default="")
    glass_id: Mapped[str] = mapped_column(Text, default="")
    carrier_id: Mapped[str] = mapped_column(Text, default="")
    # 產量
    input_qty: Mapped[float] = mapped_column(Float, default=0.0)
    output_qty: Mapped[float] = mapped_column(Float, default=0.0)
    defect_qty: Mapped[float] = mapped_column(Float, default=0.0)
    scrap_qty: Mapped[float] = mapped_column(Float, default=0.0)
    unit: Mapped[str] = mapped_column(Text, default="pcs")
    # 時間
    start_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    shift: Mapped[str] = mapped_column(Text, default="")
    # 人員 / 設備
    operator: Mapped[str] = mapped_column(Text, default="")
    equipment_id: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(Text, default="recorded", index=True)
    notes: Mapped[str] = mapped_column(Text, default="")

    param_checks: Mapped[list[ProcessParamCheck]] = relationship(
        back_populates="production_log",
        cascade="all, delete-orphan",
        order_by="ProcessParamCheck.seq",
    )


class ProcessParamCheck(AuditMixin, Base):
    """製程參數檢查 — 記錄生產過程中的關鍵參數"""
    __tablename__ = "erp_process_param_checks"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=new_id)
    production_log_id: Mapped[str] = mapped_column(
        ForeignKey("erp_production_logs.id", ondelete="CASCADE"), index=True,
    )
    seq: Mapped[int] = mapped_column(Integer, default=1)
    param_name: Mapped[str] = mapped_column(Text, index=True)
    param_value: Mapped[float] = mapped_column(Float, default=0.0)
    unit: Mapped[str] = mapped_column(Text, default="")
    lsl: Mapped[float | None] = mapped_column(Float, nullable=True)
    usl: Mapped[float | None] = mapped_column(Float, nullable=True)
    target: Mapped[float | None] = mapped_column(Float, nullable=True)
    result: Mapped[str] = mapped_column(Text, default="pass", index=True)
    measured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    measured_by: Mapped[str] = mapped_column(Text, default="")
    equipment_id: Mapped[str] = mapped_column(Text, default="")
    notes: Mapped[str] = mapped_column(Text, default="")

    production_log: Mapped[ProductionLog] = relationship(back_populates="param_checks")
