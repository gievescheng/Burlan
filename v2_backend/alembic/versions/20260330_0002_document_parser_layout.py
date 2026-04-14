"""add parser and layout columns to documents

Revision ID: 20260330_0002
Revises: 20260316_0001
Create Date: 2026-03-30 00:00:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260330_0002"
down_revision = "20260316_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("parser_name", sa.Text(), nullable=False, server_default=""))
    op.add_column("documents", sa.Column("parser_note", sa.Text(), nullable=False, server_default=""))
    op.add_column("documents", sa.Column("layout_json", sa.Text(), nullable=False, server_default=""))
    op.add_column("documents", sa.Column("layout_page_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("documents", sa.Column("layout_element_count", sa.Integer(), nullable=False, server_default="0"))


def downgrade() -> None:
    op.drop_column("documents", "layout_element_count")
    op.drop_column("documents", "layout_page_count")
    op.drop_column("documents", "layout_json")
    op.drop_column("documents", "parser_note")
    op.drop_column("documents", "parser_name")
