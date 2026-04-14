from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .base import AuditMixin, new_id, utcnow


class ProductionPlan(AuditMixin, Base):
    """生產計劃 — 排程與站點分配"""
    __tablename__ = "erp_production_plans"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=new_id)
    plan_no: Mapped[str] = mapped_column(Text, unique=True, index=True)
    work_order_id: Mapped[str] = mapped_column(
        ForeignKey("erp_work_orders.id"), index=True,
    )
    product_id: Mapped[str] = mapped_column(
        ForeignKey("erp_products.id"), index=True,
    )
    route_id: Mapped[str | None] = mapped_column(
        ForeignKey("erp_process_routes.id"), index=True, nullable=True,
    )
    planned_qty: Mapped[float] = mapped_column(Float, default=0.0)
    completed_qty: Mapped[float] = mapped_column(Float, default=0.0)
    unit: Mapped[str] = mapped_column(Text, default="pcs")
    planned_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    planned_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    shift: Mapped[str] = mapped_column(Text, default="")
    line_no: Mapped[str] = mapped_column(Text, default="")
    assigned_to: Mapped[str] = mapped_column(Text, default="")
    priority: Mapped[int] = mapped_column(Integer, default=3)
    status: Mapped[str] = mapped_column(Text, default="draft", index=True)
    notes: Mapped[str] = mapped_column(Text, default="")


class MaterialIssue(AuditMixin, Base):
    """領料單"""
    __tablename__ = "erp_material_issues"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=new_id)
    issue_no: Mapped[str] = mapped_column(Text, unique=True, index=True)
    work_order_id: Mapped[str | None] = mapped_column(
        ForeignKey("erp_work_orders.id"), index=True, nullable=True,
    )
    production_plan_id: Mapped[str | None] = mapped_column(
        ForeignKey("erp_production_plans.id"), index=True, nullable=True,
    )
    issue_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    issued_by: Mapped[str] = mapped_column(Text, default="")
    received_by: Mapped[str] = mapped_column(Text, default="")
    department: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(Text, default="draft", index=True)
    notes: Mapped[str] = mapped_column(Text, default="")

    items: Mapped[list[MaterialIssueItem]] = relationship(
        back_populates="issue",
        cascade="all, delete-orphan",
        order_by="MaterialIssueItem.seq",
    )


class MaterialIssueItem(AuditMixin, Base):
    """領料明細"""
    __tablename__ = "erp_material_issue_items"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=new_id)
    issue_id: Mapped[str] = mapped_column(
        ForeignKey("erp_material_issues.id", ondelete="CASCADE"), index=True,
    )
    product_id: Mapped[str] = mapped_column(
        ForeignKey("erp_products.id"), index=True,
    )
    seq: Mapped[int] = mapped_column(Integer, default=1)
    requested_qty: Mapped[float] = mapped_column(Float, default=0.0)
    issued_qty: Mapped[float] = mapped_column(Float, default=0.0)
    unit: Mapped[str] = mapped_column(Text, default="pcs")
    lot_no: Mapped[str] = mapped_column(Text, default="")
    warehouse: Mapped[str] = mapped_column(Text, default="")
    notes: Mapped[str] = mapped_column(Text, default="")

    issue: Mapped[MaterialIssue] = relationship(back_populates="items")
