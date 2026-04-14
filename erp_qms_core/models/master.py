from __future__ import annotations

from sqlalchemy import Float, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base
from .base import AuditMixin, new_id


class Customer(AuditMixin, Base):
    """客戶主檔"""
    __tablename__ = "erp_customers"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=new_id)
    customer_code: Mapped[str] = mapped_column(Text, unique=True, index=True)
    name: Mapped[str] = mapped_column(Text, index=True)
    short_name: Mapped[str] = mapped_column(Text, default="")
    contact_person: Mapped[str] = mapped_column(Text, default="")
    phone: Mapped[str] = mapped_column(Text, default="")
    email: Mapped[str] = mapped_column(Text, default="")
    address: Mapped[str] = mapped_column(Text, default="")
    tax_id: Mapped[str] = mapped_column(Text, default="")
    payment_terms: Mapped[str] = mapped_column(Text, default="")
    currency: Mapped[str] = mapped_column(Text, default="TWD")
    status: Mapped[str] = mapped_column(Text, default="active", index=True)
    notes: Mapped[str] = mapped_column(Text, default="")


class Supplier(AuditMixin, Base):
    """供應商主檔"""
    __tablename__ = "erp_suppliers"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=new_id)
    supplier_code: Mapped[str] = mapped_column(Text, unique=True, index=True)
    name: Mapped[str] = mapped_column(Text, index=True)
    short_name: Mapped[str] = mapped_column(Text, default="")
    contact_person: Mapped[str] = mapped_column(Text, default="")
    phone: Mapped[str] = mapped_column(Text, default="")
    email: Mapped[str] = mapped_column(Text, default="")
    address: Mapped[str] = mapped_column(Text, default="")
    tax_id: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(Text, default="")
    eval_score: Mapped[int] = mapped_column(Integer, default=0)
    eval_result: Mapped[str] = mapped_column(Text, default="")
    lead_time_days: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(Text, default="active", index=True)
    notes: Mapped[str] = mapped_column(Text, default="")


class Product(AuditMixin, Base):
    """產品主檔"""
    __tablename__ = "erp_products"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=new_id)
    product_code: Mapped[str] = mapped_column(Text, unique=True, index=True)
    name: Mapped[str] = mapped_column(Text, index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(Text, default="", index=True)
    unit: Mapped[str] = mapped_column(Text, default="pcs")
    unit_price: Mapped[float] = mapped_column(Float, default=0.0)
    currency: Mapped[str] = mapped_column(Text, default="TWD")
    spec: Mapped[str] = mapped_column(Text, default="")
    drawing_no: Mapped[str] = mapped_column(Text, default="")
    customer_part_no: Mapped[str] = mapped_column(Text, default="")
    default_route_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(Text, default="active", index=True)
    notes: Mapped[str] = mapped_column(Text, default="")
