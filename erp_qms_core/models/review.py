from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .base import AuditMixin, new_id


class ManagementReview(AuditMixin, Base):
    """管理階層審查 — ISO 9001:2015 §9.3 管理階層審查"""
    __tablename__ = "erp_management_reviews"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=new_id)
    review_no: Mapped[str] = mapped_column(Text, unique=True, index=True)
    meeting_type: Mapped[str] = mapped_column(Text, default="regular", index=True)
    # regular / emergency / follow_up
    review_period_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    review_period_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    meeting_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    chairperson: Mapped[str] = mapped_column(Text, default="")
    attendees: Mapped[str] = mapped_column(Text, default="")
    # ISO §9.3.2 審查輸入 —— a) 前次審查行動狀態
    previous_actions_status: Mapped[str] = mapped_column(Text, default="")
    # b) 內外部議題變化
    context_changes: Mapped[str] = mapped_column(Text, default="")
    # c) QMS 績效資訊（彙整）
    qms_performance_summary: Mapped[str] = mapped_column(Text, default="")
    customer_satisfaction_summary: Mapped[str] = mapped_column(Text, default="")
    process_performance: Mapped[str] = mapped_column(Text, default="")
    nc_and_ca_summary: Mapped[str] = mapped_column(Text, default="")
    audit_results_summary: Mapped[str] = mapped_column(Text, default="")
    # d) 資源充足性
    resources_adequacy: Mapped[str] = mapped_column(Text, default="")
    # e) 風險/機會行動有效性
    risks_opportunities_effectiveness: Mapped[str] = mapped_column(Text, default="")
    # f) 改善機會
    improvement_opportunities: Mapped[str] = mapped_column(Text, default="")
    # ISO §9.3.3 審查輸出
    improvement_decisions: Mapped[str] = mapped_column(Text, default="")
    qms_changes: Mapped[str] = mapped_column(Text, default="")
    resource_needs: Mapped[str] = mapped_column(Text, default="")
    # 會議紀錄與結論
    meeting_minutes: Mapped[str] = mapped_column(Text, default="")
    conclusion: Mapped[str] = mapped_column(Text, default="")
    # 狀態
    status: Mapped[str] = mapped_column(Text, default="planned", index=True)
    # planned / in_progress / closed / cancelled
    closed_by: Mapped[str] = mapped_column(Text, default="")
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")

    actions: Mapped[list[ManagementReviewAction]] = relationship(
        back_populates="review",
        cascade="all, delete-orphan",
        order_by="ManagementReviewAction.action_no",
    )


class ManagementReviewAction(AuditMixin, Base):
    """管理審查行動項目 — ISO §9.3.3 審查輸出之決議追蹤"""
    __tablename__ = "erp_management_review_actions"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=new_id)
    action_no: Mapped[str] = mapped_column(Text, unique=True, index=True)
    review_id: Mapped[str] = mapped_column(
        ForeignKey("erp_management_reviews.id", ondelete="CASCADE"), index=True,
    )
    # §9.3.3 輸出類別
    action_type: Mapped[str] = mapped_column(Text, default="improvement", index=True)
    # improvement / qms_change / resource
    description: Mapped[str] = mapped_column(Text, default="")
    responsible_dept: Mapped[str] = mapped_column(Text, default="")
    responsible_person: Mapped[str] = mapped_column(Text, default="")
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    # 執行
    completion_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    effectiveness_check: Mapped[str] = mapped_column(Text, default="")
    # 連結至 CAPA（若行動為矯正措施）
    capa_id: Mapped[str | None] = mapped_column(
        ForeignKey("erp_capas.id"), index=True, nullable=True,
    )
    # 狀態
    status: Mapped[str] = mapped_column(Text, default="open", index=True)
    # open / in_progress / completed / cancelled
    notes: Mapped[str] = mapped_column(Text, default="")

    review: Mapped[ManagementReview] = relationship(back_populates="actions")
