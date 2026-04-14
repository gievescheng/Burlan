from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .base import AuditMixin, new_id, utcnow


class SalesOrder(AuditMixin, Base):
    """銷售訂單"""
    __tablename__ = "erp_sales_orders"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=new_id)
    order_no: Mapped[str] = mapped_column(Text, unique=True, index=True)
    customer_id: Mapped[str] = mapped_column(
        ForeignKey("erp_customers.id"), index=True,
    )
    order_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    required_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    currency: Mapped[str] = mapped_column(Text, default="TWD")
    total_amount: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(Text, default="draft", index=True)
    notes: Mapped[str] = mapped_column(Text, default="")

    items: Mapped[list[SalesOrderItem]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        order_by="SalesOrderItem.seq",
    )


class SalesOrderItem(AuditMixin, Base):
    """銷售訂單明細"""
    __tablename__ = "erp_sales_order_items"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=new_id)
    order_id: Mapped[str] = mapped_column(
        ForeignKey("erp_sales_orders.id", ondelete="CASCADE"), index=True,
    )
    product_id: Mapped[str] = mapped_column(
        ForeignKey("erp_products.id"), index=True,
    )
    seq: Mapped[int] = mapped_column(Integer, default=1)
    quantity: Mapped[float] = mapped_column(Float, default=0.0)
    unit_price: Mapped[float] = mapped_column(Float, default=0.0)
    unit: Mapped[str] = mapped_column(Text, default="pcs")
    line_amount: Mapped[float] = mapped_column(Float, default=0.0)
    notes: Mapped[str] = mapped_column(Text, default="")

    order: Mapped[SalesOrder] = relationship(back_populates="items")


class WorkOrder(AuditMixin, Base):
    """工單 — 生產追蹤的核心單據"""
    __tablename__ = "erp_work_orders"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=new_id)
    wo_no: Mapped[str] = mapped_column(Text, unique=True, index=True)
    sales_order_id: Mapped[str | None] = mapped_column(
        ForeignKey("erp_sales_orders.id"), index=True, nullable=True,
    )
    sales_order_item_id: Mapped[str | None] = mapped_column(
        ForeignKey("erp_sales_order_items.id"), index=True, nullable=True,
    )
    product_id: Mapped[str] = mapped_column(
        ForeignKey("erp_products.id"), index=True,
    )
    route_id: Mapped[str | None] = mapped_column(
        ForeignKey("erp_process_routes.id"), index=True, nullable=True,
    )
    # 追蹤欄位
    lot_no: Mapped[str] = mapped_column(Text, default="", index=True)
    wafer_lot: Mapped[str] = mapped_column(Text, default="")
    glass_id: Mapped[str] = mapped_column(Text, default="")
    carrier_id: Mapped[str] = mapped_column(Text, default="")
    # 數量與排程
    planned_qty: Mapped[float] = mapped_column(Float, default=0.0)
    completed_qty: Mapped[float] = mapped_column(Float, default=0.0)
    scrap_qty: Mapped[float] = mapped_column(Float, default=0.0)
    unit: Mapped[str] = mapped_column(Text, default="pcs")
    planned_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    planned_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # 責任
    priority: Mapped[int] = mapped_column(Integer, default=3)
    assigned_to: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(Text, default="draft", index=True)
    notes: Mapped[str] = mapped_column(Text, default="")
