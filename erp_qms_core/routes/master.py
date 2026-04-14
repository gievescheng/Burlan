from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .. import database
from ..schemas.master import (
    CustomerCreate, CustomerOut, CustomerUpdate,
    ProductCreate, ProductOut, ProductUpdate,
    SupplierCreate, SupplierOut, SupplierUpdate,
)
from ..services import master as svc

router = APIRouter()


# ── Customer ────────────────────────────────────────────

@router.get("/customers", response_model=list[CustomerOut])
def list_customers(status: str | None = None):
    with database.session_scope() as s:
        return svc.list_customers(s, status=status)


@router.get("/customers/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: str):
    with database.session_scope() as s:
        row = svc.get_customer(s, customer_id)
    if not row:
        raise HTTPException(404, "Customer not found")
    return row


@router.post("/customers", response_model=CustomerOut, status_code=201)
def create_customer(body: CustomerCreate):
    try:
        with database.session_scope() as s:
            return svc.create_customer(s, body.model_dump())
    except ValueError as e:
        raise HTTPException(409, str(e))


@router.patch("/customers/{customer_id}", response_model=CustomerOut)
def update_customer(customer_id: str, body: CustomerUpdate):
    with database.session_scope() as s:
        row = svc.update_customer(s, customer_id, body.model_dump(exclude_unset=True))
    if not row:
        raise HTTPException(404, "Customer not found")
    return row


@router.delete("/customers/{customer_id}", status_code=204)
def delete_customer(customer_id: str):
    with database.session_scope() as s:
        if not svc.delete_customer(s, customer_id):
            raise HTTPException(404, "Customer not found")


# ── Supplier ────────────────────────────────────────────

@router.get("/suppliers", response_model=list[SupplierOut])
def list_suppliers(status: str | None = None):
    with database.session_scope() as s:
        return svc.list_suppliers(s, status=status)


@router.get("/suppliers/{supplier_id}", response_model=SupplierOut)
def get_supplier(supplier_id: str):
    with database.session_scope() as s:
        row = svc.get_supplier(s, supplier_id)
    if not row:
        raise HTTPException(404, "Supplier not found")
    return row


@router.post("/suppliers", response_model=SupplierOut, status_code=201)
def create_supplier(body: SupplierCreate):
    try:
        with database.session_scope() as s:
            return svc.create_supplier(s, body.model_dump())
    except ValueError as e:
        raise HTTPException(409, str(e))


@router.patch("/suppliers/{supplier_id}", response_model=SupplierOut)
def update_supplier(supplier_id: str, body: SupplierUpdate):
    with database.session_scope() as s:
        row = svc.update_supplier(s, supplier_id, body.model_dump(exclude_unset=True))
    if not row:
        raise HTTPException(404, "Supplier not found")
    return row


@router.delete("/suppliers/{supplier_id}", status_code=204)
def delete_supplier(supplier_id: str):
    with database.session_scope() as s:
        if not svc.delete_supplier(s, supplier_id):
            raise HTTPException(404, "Supplier not found")


# ── Product ─────────────────────────────────────────────

@router.get("/products", response_model=list[ProductOut])
def list_products(status: str | None = None, category: str | None = None):
    with database.session_scope() as s:
        return svc.list_products(s, status=status, category=category)


@router.get("/products/{product_id}", response_model=ProductOut)
def get_product(product_id: str):
    with database.session_scope() as s:
        row = svc.get_product(s, product_id)
    if not row:
        raise HTTPException(404, "Product not found")
    return row


@router.post("/products", response_model=ProductOut, status_code=201)
def create_product(body: ProductCreate):
    try:
        with database.session_scope() as s:
            return svc.create_product(s, body.model_dump())
    except ValueError as e:
        raise HTTPException(409, str(e))


@router.patch("/products/{product_id}", response_model=ProductOut)
def update_product(product_id: str, body: ProductUpdate):
    with database.session_scope() as s:
        row = svc.update_product(s, product_id, body.model_dump(exclude_unset=True))
    if not row:
        raise HTTPException(404, "Product not found")
    return row


@router.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: str):
    with database.session_scope() as s:
        if not svc.delete_product(s, product_id):
            raise HTTPException(404, "Product not found")
