from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .base import AuditMixin, new_id


class Document(AuditMixin, Base):
    """受控文件主檔 — ISO 9001:2015 §7.5 文件化資訊"""
    __tablename__ = "erp_documents"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=new_id)
    document_no: Mapped[str] = mapped_column(Text, unique=True, index=True)
    title: Mapped[str] = mapped_column(Text, default="")
    # ISO §7.5.1 文件類別
    category: Mapped[str] = mapped_column(Text, default="procedure", index=True)
    # manual / policy / procedure / work_instruction / form / record / specification / drawing
    classification: Mapped[str] = mapped_column(Text, default="controlled", index=True)
    # controlled / uncontrolled / confidential
    # 擁有者
    owner: Mapped[str] = mapped_column(Text, default="")
    department: Mapped[str] = mapped_column(Text, default="", index=True)
    # 目前有效版本（指向 DocumentRevision.revision）
    current_revision: Mapped[str] = mapped_column(Text, default="")
    # 狀態
    status: Mapped[str] = mapped_column(Text, default="active", index=True)
    # active / inactive / archived
    description: Mapped[str] = mapped_column(Text, default="")
    notes: Mapped[str] = mapped_column(Text, default="")

    revisions: Mapped[list[DocumentRevision]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="DocumentRevision.revision",
    )


class DocumentRevision(AuditMixin, Base):
    """文件版本 — ISO 9001:2015 §7.5.2 / §7.5.3 版本控制與審查核准"""
    __tablename__ = "erp_document_revisions"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=new_id)
    document_id: Mapped[str] = mapped_column(
        ForeignKey("erp_documents.id", ondelete="CASCADE"), index=True,
    )
    revision: Mapped[str] = mapped_column(Text, index=True)
    # 變更說明
    change_summary: Mapped[str] = mapped_column(Text, default="")
    change_reason: Mapped[str] = mapped_column(Text, default="")
    # ISO §7.5.2 b) 審查與核准 — 以角色分離呈現
    prepared_by: Mapped[str] = mapped_column(Text, default="")
    prepared_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_by: Mapped[str] = mapped_column(Text, default="")
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_by: Mapped[str] = mapped_column(Text, default="")
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # ISO §7.5.3 發行/廢止日期
    effective_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    obsolete_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    # 實體檔案（留作連結或路徑）
    file_path: Mapped[str] = mapped_column(Text, default="")
    file_checksum: Mapped[str] = mapped_column(Text, default="")
    # 狀態
    status: Mapped[str] = mapped_column(Text, default="draft", index=True)
    # draft / under_review / approved / effective / superseded / obsolete / cancelled
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    notes: Mapped[str] = mapped_column(Text, default="")

    document: Mapped[Document] = relationship(back_populates="revisions")
