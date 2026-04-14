"""Add Documents and Training (ISO 9001:2015 §7.5 + §7.2)

Revision ID: erp_0008
Revises: erp_0007
Create Date: 2026-04-14
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "erp_0008"
down_revision = "erp_0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── erp_documents ───────────────────────────────────
    op.create_table(
        "erp_documents",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("document_no", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False, server_default=""),
        sa.Column("category", sa.Text(), nullable=False, server_default="procedure"),
        sa.Column("classification", sa.Text(), nullable=False, server_default="controlled"),
        sa.Column("owner", sa.Text(), nullable=False, server_default=""),
        sa.Column("department", sa.Text(), nullable=False, server_default=""),
        sa.Column("current_revision", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.Text(), nullable=False, server_default="active"),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("updated_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_erp_documents_document_no", "erp_documents", ["document_no"], unique=True)
    op.create_index("ix_erp_documents_category", "erp_documents", ["category"])
    op.create_index("ix_erp_documents_classification", "erp_documents", ["classification"])
    op.create_index("ix_erp_documents_department", "erp_documents", ["department"])
    op.create_index("ix_erp_documents_status", "erp_documents", ["status"])

    # ── erp_document_revisions ──────────────────────────
    op.create_table(
        "erp_document_revisions",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column(
            "document_id",
            sa.Text(),
            sa.ForeignKey("erp_documents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("revision", sa.Text(), nullable=False),
        sa.Column("change_summary", sa.Text(), nullable=False, server_default=""),
        sa.Column("change_reason", sa.Text(), nullable=False, server_default=""),
        sa.Column("prepared_by", sa.Text(), nullable=False, server_default=""),
        sa.Column("prepared_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_by", sa.Text(), nullable=False, server_default=""),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_by", sa.Text(), nullable=False, server_default=""),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("effective_date", sa.Date(), nullable=True),
        sa.Column("obsolete_date", sa.Date(), nullable=True),
        sa.Column("file_path", sa.Text(), nullable=False, server_default=""),
        sa.Column("file_checksum", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.Text(), nullable=False, server_default="draft"),
        sa.Column("is_current", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("updated_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_erp_document_revisions_document_id", "erp_document_revisions", ["document_id"])
    op.create_index("ix_erp_document_revisions_revision", "erp_document_revisions", ["revision"])
    op.create_index("ix_erp_document_revisions_effective_date", "erp_document_revisions", ["effective_date"])
    op.create_index("ix_erp_document_revisions_status", "erp_document_revisions", ["status"])
    op.create_index("ix_erp_document_revisions_is_current", "erp_document_revisions", ["is_current"])

    # ── erp_training_courses ────────────────────────────
    op.create_table(
        "erp_training_courses",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("course_no", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False, server_default=""),
        sa.Column("category", sa.Text(), nullable=False, server_default="technical"),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("prerequisites", sa.Text(), nullable=False, server_default=""),
        sa.Column("required_for", sa.Text(), nullable=False, server_default=""),
        sa.Column("duration_hours", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("validity_months", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("passing_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column(
            "related_document_id",
            sa.Text(),
            sa.ForeignKey("erp_documents.id"),
            nullable=True,
        ),
        sa.Column("status", sa.Text(), nullable=False, server_default="active"),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("updated_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_erp_training_courses_course_no", "erp_training_courses", ["course_no"], unique=True)
    op.create_index("ix_erp_training_courses_category", "erp_training_courses", ["category"])
    op.create_index("ix_erp_training_courses_related_document_id", "erp_training_courses", ["related_document_id"])
    op.create_index("ix_erp_training_courses_status", "erp_training_courses", ["status"])

    # ── erp_training_records ────────────────────────────
    op.create_table(
        "erp_training_records",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("record_no", sa.Text(), nullable=False),
        sa.Column(
            "course_id",
            sa.Text(),
            sa.ForeignKey("erp_training_courses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("employee_id", sa.Text(), nullable=False),
        sa.Column("employee_name", sa.Text(), nullable=False, server_default=""),
        sa.Column("department", sa.Text(), nullable=False, server_default=""),
        sa.Column("position", sa.Text(), nullable=False, server_default=""),
        sa.Column("training_type", sa.Text(), nullable=False, server_default="classroom"),
        sa.Column("trainer", sa.Text(), nullable=False, server_default=""),
        sa.Column("training_date", sa.Date(), nullable=True),
        sa.Column("completed_date", sa.Date(), nullable=True),
        sa.Column("score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("passed", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("certificate_no", sa.Text(), nullable=False, server_default=""),
        sa.Column("expiry_date", sa.Date(), nullable=True),
        sa.Column("verified_by", sa.Text(), nullable=False, server_default=""),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("updated_by", sa.Text(), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_erp_training_records_record_no", "erp_training_records", ["record_no"], unique=True)
    op.create_index("ix_erp_training_records_course_id", "erp_training_records", ["course_id"])
    op.create_index("ix_erp_training_records_employee_id", "erp_training_records", ["employee_id"])
    op.create_index("ix_erp_training_records_department", "erp_training_records", ["department"])
    op.create_index("ix_erp_training_records_training_type", "erp_training_records", ["training_type"])
    op.create_index("ix_erp_training_records_training_date", "erp_training_records", ["training_date"])
    op.create_index("ix_erp_training_records_passed", "erp_training_records", ["passed"])
    op.create_index("ix_erp_training_records_expiry_date", "erp_training_records", ["expiry_date"])


def downgrade() -> None:
    op.drop_table("erp_training_records")
    op.drop_table("erp_training_courses")
    op.drop_table("erp_document_revisions")
    op.drop_table("erp_documents")
