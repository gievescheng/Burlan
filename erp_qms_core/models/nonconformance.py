from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .base import AuditMixin, new_id


class NCR(AuditMixin, Base):
    """不合格品報告 — ISO 9001:2015 §8.7 不合格品輸出管制"""
    __tablename__ = "erp_ncrs"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=new_id)
    ncr_no: Mapped[str] = mapped_column(Text, unique=True, index=True)
    # 來源
    work_order_id: Mapped[str] = mapped_column(
        ForeignKey("erp_work_orders.id"), index=True,
    )
    product_id: Mapped[str] = mapped_column(
        ForeignKey("erp_products.id"), index=True,
    )
    inspection_lot_id: Mapped[str | None] = mapped_column(
        ForeignKey("erp_inspection_lots.id"), index=True, nullable=True,
    )
    production_log_id: Mapped[str | None] = mapped_column(
        ForeignKey("erp_production_logs.id"), index=True, nullable=True,
    )
    station_id: Mapped[str | None] = mapped_column(
        ForeignKey("erp_process_stations.id"), index=True, nullable=True,
    )
    # 追蹤
    lot_no: Mapped[str] = mapped_column(Text, default="", index=True)
    wafer_lot: Mapped[str] = mapped_column(Text, default="")
    glass_id: Mapped[str] = mapped_column(Text, default="")
    carrier_id: Mapped[str] = mapped_column(Text, default="")
    # 數量
    defect_qty: Mapped[float] = mapped_column(Float, default=0.0)
    total_qty: Mapped[float] = mapped_column(Float, default=0.0)
    # 缺陷描述
    defect_code: Mapped[str] = mapped_column(Text, default="", index=True)
    defect_description: Mapped[str] = mapped_column(Text, default="")
    severity: Mapped[str] = mapped_column(Text, default="minor", index=True)
    # critical / major / minor
    category: Mapped[str] = mapped_column(Text, default="process", index=True)
    # process / material / equipment / human / design / external
    # 處置 (ISO 8.7 — 必須記錄處置決議)
    disposition: Mapped[str] = mapped_column(Text, default="", index=True)
    # rework / scrap / return_to_supplier / concession / use_as_is / regrade
    disposition_reason: Mapped[str] = mapped_column(Text, default="")
    disposition_by: Mapped[str] = mapped_column(Text, default="")
    disposition_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # 狀態
    status: Mapped[str] = mapped_column(Text, default="open", index=True)
    # open / under_review / disposition_decided / in_action / closed / cancelled
    # 人員時間
    reported_by: Mapped[str] = mapped_column(Text, default="")
    reported_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    assigned_to: Mapped[str] = mapped_column(Text, default="")
    closed_by: Mapped[str] = mapped_column(Text, default="")
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # 後續
    requires_capa: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    notes: Mapped[str] = mapped_column(Text, default="")

    rework_orders: Mapped[list[ReworkOrder]] = relationship(
        back_populates="ncr",
        cascade="all, delete-orphan",
        order_by="ReworkOrder.rework_no",
    )


class ReworkOrder(AuditMixin, Base):
    """重工單 — NCR 處置為 rework 時建立"""
    __tablename__ = "erp_rework_orders"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=new_id)
    rework_no: Mapped[str] = mapped_column(Text, unique=True, index=True)
    ncr_id: Mapped[str] = mapped_column(
        ForeignKey("erp_ncrs.id", ondelete="CASCADE"), index=True,
    )
    work_order_id: Mapped[str] = mapped_column(
        ForeignKey("erp_work_orders.id"), index=True,
    )
    product_id: Mapped[str] = mapped_column(
        ForeignKey("erp_products.id"), index=True,
    )
    # 數量
    rework_qty: Mapped[float] = mapped_column(Float, default=0.0)
    success_qty: Mapped[float] = mapped_column(Float, default=0.0)
    scrap_qty: Mapped[float] = mapped_column(Float, default=0.0)
    # 重工方法
    method: Mapped[str] = mapped_column(Text, default="")
    instructions: Mapped[str] = mapped_column(Text, default="")
    # 執行
    assigned_to: Mapped[str] = mapped_column(Text, default="")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # 狀態
    status: Mapped[str] = mapped_column(Text, default="planned", index=True)
    # planned / in_progress / completed / cancelled
    result: Mapped[str] = mapped_column(Text, default="", index=True)
    # passed / failed (成果判定)
    # 後續檢驗追溯（ISO 8.7：經處置後須再次驗證符合性）
    reinspection_lot_id: Mapped[str | None] = mapped_column(
        ForeignKey("erp_inspection_lots.id"), nullable=True, index=True,
    )
    notes: Mapped[str] = mapped_column(Text, default="")

    ncr: Mapped[NCR] = relationship(back_populates="rework_orders")
