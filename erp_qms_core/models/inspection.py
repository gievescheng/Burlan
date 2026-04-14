from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .base import AuditMixin, new_id, utcnow


class InspectionLot(AuditMixin, Base):
    """檢驗批 — ISO 9001:2015 §8.6 產品放行依據"""
    __tablename__ = "erp_inspection_lots"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=new_id)
    lot_no: Mapped[str] = mapped_column(Text, unique=True, index=True)
    # 來源
    work_order_id: Mapped[str] = mapped_column(
        ForeignKey("erp_work_orders.id"), index=True,
    )
    production_log_id: Mapped[str | None] = mapped_column(
        ForeignKey("erp_production_logs.id"), index=True, nullable=True,
    )
    product_id: Mapped[str] = mapped_column(
        ForeignKey("erp_products.id"), index=True,
    )
    station_id: Mapped[str | None] = mapped_column(
        ForeignKey("erp_process_stations.id"), index=True, nullable=True,
    )
    # 追蹤
    source_lot_no: Mapped[str] = mapped_column(Text, default="", index=True)
    wafer_lot: Mapped[str] = mapped_column(Text, default="")
    glass_id: Mapped[str] = mapped_column(Text, default="")
    carrier_id: Mapped[str] = mapped_column(Text, default="")
    # 抽樣計畫（ISO 8.6 — 要保留檢驗紀錄）
    inspection_type: Mapped[str] = mapped_column(Text, default="in_process", index=True)
    # incoming / in_process / final / random
    sample_plan: Mapped[str] = mapped_column(Text, default="")
    total_qty: Mapped[float] = mapped_column(Float, default=0.0)
    sample_size: Mapped[float] = mapped_column(Float, default=0.0)
    accept_qty: Mapped[float] = mapped_column(Float, default=0.0)
    reject_qty: Mapped[float] = mapped_column(Float, default=0.0)
    # 狀態與處置
    status: Mapped[str] = mapped_column(Text, default="pending", index=True)
    # pending / in_progress / passed / failed / conditional / closed / cancelled
    disposition: Mapped[str] = mapped_column(Text, default="", index=True)
    # release / hold / reject / concession / rework
    # 人員時間
    inspector: Mapped[str] = mapped_column(Text, default="")
    inspected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_by: Mapped[str] = mapped_column(Text, default="")
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")

    results: Mapped[list[InspectionResult]] = relationship(
        back_populates="inspection_lot",
        cascade="all, delete-orphan",
        order_by="InspectionResult.seq",
    )


class InspectionResult(AuditMixin, Base):
    """檢驗結果 — 單一檢驗項目實測"""
    __tablename__ = "erp_inspection_results"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=new_id)
    inspection_lot_id: Mapped[str] = mapped_column(
        ForeignKey("erp_inspection_lots.id", ondelete="CASCADE"), index=True,
    )
    seq: Mapped[int] = mapped_column(Integer, default=1)
    item_name: Mapped[str] = mapped_column(Text, index=True)
    spec_value: Mapped[str] = mapped_column(Text, default="")
    # 數值規格 + 實測
    lsl: Mapped[float | None] = mapped_column(Float, nullable=True)
    usl: Mapped[float | None] = mapped_column(Float, nullable=True)
    target: Mapped[float | None] = mapped_column(Float, nullable=True)
    actual_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    # 文字實測（外觀檢驗常用：OK/NG）
    actual_text: Mapped[str] = mapped_column(Text, default="")
    unit: Mapped[str] = mapped_column(Text, default="")
    equipment_id: Mapped[str] = mapped_column(Text, default="")
    # 判定
    result: Mapped[str] = mapped_column(Text, default="pass", index=True)
    # pass / fail / n_a
    defect_code: Mapped[str] = mapped_column(Text, default="")
    defect_qty: Mapped[float] = mapped_column(Float, default=0.0)
    measured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    measured_by: Mapped[str] = mapped_column(Text, default="")
    notes: Mapped[str] = mapped_column(Text, default="")

    inspection_lot: Mapped[InspectionLot] = relationship(back_populates="results")
