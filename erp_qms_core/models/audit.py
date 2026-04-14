from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .base import AuditMixin, new_id


class InternalAudit(AuditMixin, Base):
    """內部稽核 — ISO 9001:2015 §9.2 內部稽核"""
    __tablename__ = "erp_internal_audits"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=new_id)
    audit_no: Mapped[str] = mapped_column(Text, unique=True, index=True)
    # ISO §9.2.2 a) 稽核類型
    audit_type: Mapped[str] = mapped_column(Text, default="planned", index=True)
    # planned / unannounced / follow_up / special
    # ISO §9.2.2 b) 稽核範圍與準則
    scope: Mapped[str] = mapped_column(Text, default="process", index=True)
    # process / department / clause / full_system
    audit_criteria: Mapped[str] = mapped_column(Text, default="")
    # 例如：ISO 9001:2015 §7.5, §8.5；公司程序書 QP-01
    scope_description: Mapped[str] = mapped_column(Text, default="")
    # 受稽核單位
    department: Mapped[str] = mapped_column(Text, default="", index=True)
    # ISO §9.2.2 c) 稽核員（須確保客觀性與公正性）
    lead_auditor: Mapped[str] = mapped_column(Text, default="")
    auditors: Mapped[str] = mapped_column(Text, default="")
    # 排程
    planned_start_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    planned_end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    actual_start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    actual_end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    # 狀態
    status: Mapped[str] = mapped_column(Text, default="planned", index=True)
    # planned / in_progress / reporting / closed / cancelled
    # ISO §9.2.2 d) 報告
    report_summary: Mapped[str] = mapped_column(Text, default="")
    conclusion: Mapped[str] = mapped_column(Text, default="")
    reported_to: Mapped[str] = mapped_column(Text, default="")
    reported_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # 發現統計（便於儀表板查詢）
    total_findings: Mapped[int] = mapped_column(Integer, default=0)
    major_findings_count: Mapped[int] = mapped_column(Integer, default=0)
    minor_findings_count: Mapped[int] = mapped_column(Integer, default=0)
    observation_count: Mapped[int] = mapped_column(Integer, default=0)
    # 結案
    closed_by: Mapped[str] = mapped_column(Text, default="")
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")

    findings: Mapped[list[AuditFinding]] = relationship(
        back_populates="audit",
        cascade="all, delete-orphan",
        order_by="AuditFinding.finding_no",
    )


class AuditFinding(AuditMixin, Base):
    """稽核發現 — ISO 9001:2015 §9.2.2 e) 發現須追蹤至改善"""
    __tablename__ = "erp_audit_findings"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=new_id)
    finding_no: Mapped[str] = mapped_column(Text, unique=True, index=True)
    audit_id: Mapped[str] = mapped_column(
        ForeignKey("erp_internal_audits.id", ondelete="CASCADE"), index=True,
    )
    # ISO 條款關聯
    clause: Mapped[str] = mapped_column(Text, default="", index=True)
    # 例如：7.5.2, 8.5.1
    finding_type: Mapped[str] = mapped_column(Text, default="observation", index=True)
    # major_nc / minor_nc / observation / opportunity
    # 事實與證據
    description: Mapped[str] = mapped_column(Text, default="")
    evidence: Mapped[str] = mapped_column(Text, default="")
    root_cause: Mapped[str] = mapped_column(Text, default="")
    # ISO §9.2.2 e) 後續矯正
    requires_capa: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    capa_id: Mapped[str | None] = mapped_column(
        ForeignKey("erp_capas.id"), index=True, nullable=True,
    )
    # 受稽單位回覆與改善
    responsible_dept: Mapped[str] = mapped_column(Text, default="")
    responsible_person: Mapped[str] = mapped_column(Text, default="")
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    response_text: Mapped[str] = mapped_column(Text, default="")
    # 驗證
    verified_by: Mapped[str] = mapped_column(Text, default="")
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # 狀態
    status: Mapped[str] = mapped_column(Text, default="open", index=True)
    # open / corrective_action / verified / closed / cancelled
    closed_by: Mapped[str] = mapped_column(Text, default="")
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")

    audit: Mapped[InternalAudit] = relationship(back_populates="findings")
