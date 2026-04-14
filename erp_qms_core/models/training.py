from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .base import AuditMixin, new_id


class TrainingCourse(AuditMixin, Base):
    """訓練課程 — ISO 9001:2015 §7.2 能力（Competence）"""
    __tablename__ = "erp_training_courses"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=new_id)
    course_no: Mapped[str] = mapped_column(Text, unique=True, index=True)
    title: Mapped[str] = mapped_column(Text, default="")
    # 課程類別
    category: Mapped[str] = mapped_column(Text, default="technical", index=True)
    # orientation / technical / safety / quality / iso_awareness / compliance / other
    description: Mapped[str] = mapped_column(Text, default="")
    prerequisites: Mapped[str] = mapped_column(Text, default="")
    # 適用對象（自由文字：角色/部門/職位）
    required_for: Mapped[str] = mapped_column(Text, default="")
    # 課程規格
    duration_hours: Mapped[float] = mapped_column(Float, default=0.0)
    # 合格有效期（月），0 = 不過期
    validity_months: Mapped[int] = mapped_column(Integer, default=0)
    # 通過門檻分數
    passing_score: Mapped[float] = mapped_column(Float, default=0.0)
    # 連結至 SOP / 訓練教材文件
    related_document_id: Mapped[str | None] = mapped_column(
        ForeignKey("erp_documents.id"), index=True, nullable=True,
    )
    # 狀態
    status: Mapped[str] = mapped_column(Text, default="active", index=True)
    # active / inactive / archived
    notes: Mapped[str] = mapped_column(Text, default="")

    records: Mapped[list[TrainingRecord]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan",
        order_by="TrainingRecord.record_no",
    )


class TrainingRecord(AuditMixin, Base):
    """訓練紀錄 — ISO 9001:2015 §7.2 d) 能力佐證之文件化資訊"""
    __tablename__ = "erp_training_records"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=new_id)
    record_no: Mapped[str] = mapped_column(Text, unique=True, index=True)
    course_id: Mapped[str] = mapped_column(
        ForeignKey("erp_training_courses.id", ondelete="CASCADE"), index=True,
    )
    # 受訓人員（保留文字，未來可接員工主檔）
    employee_id: Mapped[str] = mapped_column(Text, index=True)
    employee_name: Mapped[str] = mapped_column(Text, default="")
    department: Mapped[str] = mapped_column(Text, default="", index=True)
    position: Mapped[str] = mapped_column(Text, default="")
    # 實施
    training_type: Mapped[str] = mapped_column(Text, default="classroom", index=True)
    # classroom / on_the_job / e_learning / external / self_study
    trainer: Mapped[str] = mapped_column(Text, default="")
    training_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    completed_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    # 成績
    score: Mapped[float] = mapped_column(Float, default=0.0)
    passed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    # ISO §7.2 d) 能力有效期
    certificate_no: Mapped[str] = mapped_column(Text, default="")
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    # 覆核（主管簽署確認能力達成）
    verified_by: Mapped[str] = mapped_column(Text, default="")
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")

    course: Mapped[TrainingCourse] = relationship(back_populates="records")
