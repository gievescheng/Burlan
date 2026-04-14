from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


# ── Customer ────────────────────────────────────────────

class CustomerCreate(BaseModel):
    customer_code: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    short_name: str = ""
    contact_person: str = ""
    phone: str = ""
    email: str = ""
    address: str = ""
    tax_id: str = ""
    payment_terms: str = ""
    currency: str = "TWD"
    notes: str = ""


class CustomerUpdate(BaseModel):
    name: str | None = None
    short_name: str | None = None
    contact_person: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    tax_id: str | None = None
    payment_terms: str | None = None
    currency: str | None = None
    status: str | None = None
    notes: str | None = None


class CustomerOut(BaseModel):
    id: str
    customer_code: str
    name: str
    short_name: str
    contact_person: str
    phone: str
    email: str
    address: str
    tax_id: str
    payment_terms: str
    currency: str
    status: str
    notes: str
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Supplier ────────────────────────────────────────────

class SupplierCreate(BaseModel):
    supplier_code: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    short_name: str = ""
    contact_person: str = ""
    phone: str = ""
    email: str = ""
    address: str = ""
    tax_id: str = ""
    category: str = ""
    lead_time_days: int = 0
    notes: str = ""


class SupplierUpdate(BaseModel):
    name: str | None = None
    short_name: str | None = None
    contact_person: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    tax_id: str | None = None
    category: str | None = None
    eval_score: int | None = None
    eval_result: str | None = None
    lead_time_days: int | None = None
    status: str | None = None
    notes: str | None = None


class SupplierOut(BaseModel):
    id: str
    supplier_code: str
    name: str
    short_name: str
    contact_person: str
    phone: str
    email: str
    address: str
    tax_id: str
    category: str
    eval_score: int
    eval_result: str
    lead_time_days: int
    status: str
    notes: str
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Product ─────────────────────────────────────────────

class ProductCreate(BaseModel):
    product_code: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    description: str = ""
    category: str = ""
    unit: str = "pcs"
    unit_price: float = 0.0
    currency: str = "TWD"
    spec: str = ""
    drawing_no: str = ""
    customer_part_no: str = ""
    default_route_id: str | None = None
    notes: str = ""


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category: str | None = None
    unit: str | None = None
    unit_price: float | None = None
    currency: str | None = None
    spec: str | None = None
    drawing_no: str | None = None
    customer_part_no: str | None = None
    default_route_id: str | None = None
    status: str | None = None
    notes: str | None = None


class ProductOut(BaseModel):
    id: str
    product_code: str
    name: str
    description: str
    category: str
    unit: str
    unit_price: float
    currency: str
    spec: str
    drawing_no: str
    customer_part_no: str
    default_route_id: str | None
    status: str
    notes: str
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
