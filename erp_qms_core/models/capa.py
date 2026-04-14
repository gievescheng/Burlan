from __future__ import annotations

from datetime import datetime, date

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base
from .base import AuditMixin, new_id


class CustomerComplaint(AuditMixin, Base):
    """客訴 — ISO 9001:2015 §9.1.2 顧客滿意度 + §10.2 矯正措施觸發來源"""
    __tablename__ = "erp_customer_complaints"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=new_id)
    complaint_no: Mapped[str] = mapped_column(Text, unique=True, index=True)
    # 來源
    customer_id: Mapped[str] = mapped_column(
        ForeignKey("erp_customers.id"), index=True,
    )
    product_id: Mapped[str] = mapped_column(
        ForeignKey("erp_products.id"), index=True,
    )
    sales_order_id: Mapped[str | None] = mapped_column(
        ForeignKey("erp_sales_orders.id"), index=True, nullable=True,
    )
    work_order_id: Mapped[str | None] = mapped_column(
        ForeignKey("erp_work_orders.id"), index=True, nullable=True,
    )
    # 追蹤
    lot_no: Mapped[str] = mapped_column(Text, default="", index=True)
    delivery_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    claimed_qty: Mapped[float] = mapped_column(Float, default=0.0)
    # 客訴內容
    complaint_type: Mapped[str] = mapped_column(Text, default="quality", index=True)
    # quality / delivery / service / documentation / other
    severity: Mapped[str] = mapped_column(Text, default="minor", index=True)
    # critical / major / minor
    subject: Mapped[str] = mapped_column(Text, default="")
    description: Mapped[str] = mapped_column(Text, default="")
    customer_contact: Mapped[str] = mapped_column(Text, default="")
    # 接收
    channel: Mapped[str] = mapped_column(Text, default="email")
    # email / phone / portal / visit / other
    received_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    received_by: Mapped[str] = mapped_column(Text, default="")
    # 處理狀態
    status: Mapped[str] = mapped_column(Text, default="received", index=True)
    # received / under_investigation / responding / resolved / closed / cancelled
    # 答覆
    response_text: Mapped[str] = mapped_column(Text, default="")
    responded_by: Mapped[str] = mapped_column(Text, default="")
    responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # 結案
    closed_by: Mapped[str] = mapped_column(Text, default="")
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    customer_satisfied: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    # 後續
    requires_capa: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    notes: Mapped[str] = mapped_column(Text, default="")


class CAPA(AuditMixin, Base):
    """矯正/預防措施 — ISO 9001:2015 §10.2 不符合與矯正措施"""
    __tablename__ = "erp_capas"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=new_id)
    capa_no: Mapped[str] = mapped_column(Text, unique=True, index=True)
    capa_type: Mapped[str] = mapped_column(Text, default="corrective", index=True)
    # corrective / preventive
    # 來源（多型 — 可同時連結結構化 FK 與自由 source 描述）
    source_type: Mapped[str] = mapped_column(Text, default="ncr", index=True)
    # ncr / complaint / audit / management_review / other
    ncr_id: Mapped[str | None] = mapped_column(
        ForeignKey("erp_ncrs.id"), index=True, nullable=True,
    )
    complaint_id: Mapped[str | None] = mapped_column(
        ForeignKey("erp_customer_complaints.id"), index=True, nullable=True,
    )
    source_ref: Mapped[str] = mapped_column(Text, default="")
    # 主題
    subject: Mapped[str] = mapped_column(Text, default="")
    description: Mapped[str] = mapped_column(Text, default="")
    severity: Mapped[str] = mapped_column(Text, default="minor", index=True)
    # critical / major / minor
    # ISO §10.2.1 b)2) 根因分析
    root_cause_method: Mapped[str] = mapped_column(Text, default="5why")
    # 5why / ishikawa / 8d / fmea / other
    root_cause: Mapped[str] = mapped_column(Text, default="")
    # ISO §10.2.1 b)3) 是否存在類似問題
    similar_issues_check: Mapped[str] = mapped_column(Text, default="")
    # ISO §10.2.1 c) 行動計畫
    containment_action: Mapped[str] = mapped_column(Text, default="")
    corrective_action: Mapped[str] = mapped_column(Text, default="")
    preventive_action: Mapped[str] = mapped_column(Text, default="")
    # 執行
    assigned_to: Mapped[str] = mapped_column(Text, default="")
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # ISO §10.2.1 d) 有效性驗證
    effectiveness_check: Mapped[str] = mapped_column(Text, default="")
    effectiveness_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_by: Mapped[str] = mapped_column(Text, default="")
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # ISO §10.2.1 e) 風險更新
    risk_updated: Mapped[bool] = mapped_column(Boolean, default=False)
    # ISO §10.2.1 f) QMS 變更
    qms_changes_required: Mapped[bool] = mapped_column(Boolean, default=False)
    # 狀態
    status: Mapped[str] = mapped_column(Text, default="open", index=True)
    # open / in_progress / verifying / closed / cancelled
    closed_by: Mapped[str] = mapped_column(Text, default="")
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")
