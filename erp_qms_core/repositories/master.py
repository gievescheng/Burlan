from __future__ import annotations

from sqlalchemy.orm import Session

from ..models.master import Customer, Product, Supplier


# ── Customer ────────────────────────────────────────────

def list_customers(session: Session, *, status: str | None = None) -> list[Customer]:
    q = session.query(Customer)
    if status:
        q = q.filter(Customer.status == status)
    return q.order_by(Customer.customer_code).all()


def get_customer(session: Session, customer_id: str) -> Customer | None:
    return session.get(Customer, customer_id)


def get_customer_by_code(session: Session, code: str) -> Customer | None:
    return session.query(Customer).filter(Customer.customer_code == code).first()


def create_customer(session: Session, data: dict) -> Customer:
    obj = Customer(**data)
    session.add(obj)
    session.flush()
    return obj


def update_customer(session: Session, customer_id: str, data: dict) -> Customer | None:
    obj = session.get(Customer, customer_id)
    if not obj:
        return None
    for k, v in data.items():
        if v is not None:
            setattr(obj, k, v)
    session.flush()
    return obj


def delete_customer(session: Session, customer_id: str) -> bool:
    obj = session.get(Customer, customer_id)
    if not obj:
        return False
    session.delete(obj)
    session.flush()
    return True


# ── Supplier ────────────────────────────────────────────

def list_suppliers(session: Session, *, status: str | None = None) -> list[Supplier]:
    q = session.query(Supplier)
    if status:
        q = q.filter(Supplier.status == status)
    return q.order_by(Supplier.supplier_code).all()


def get_supplier(session: Session, supplier_id: str) -> Supplier | None:
    return session.get(Supplier, supplier_id)


def get_supplier_by_code(session: Session, code: str) -> Supplier | None:
    return session.query(Supplier).filter(Supplier.supplier_code == code).first()


def create_supplier(session: Session, data: dict) -> Supplier:
    obj = Supplier(**data)
    session.add(obj)
    session.flush()
    return obj


def update_supplier(session: Session, supplier_id: str, data: dict) -> Supplier | None:
    obj = session.get(Supplier, supplier_id)
    if not obj:
        return None
    for k, v in data.items():
        if v is not None:
            setattr(obj, k, v)
    session.flush()
    return obj


def delete_supplier(session: Session, supplier_id: str) -> bool:
    obj = session.get(Supplier, supplier_id)
    if not obj:
        return False
    session.delete(obj)
    session.flush()
    return True


# ── Product ─────────────────────────────────────────────

def list_products(session: Session, *, status: str | None = None, category: str | None = None) -> list[Product]:
    q = session.query(Product)
    if status:
        q = q.filter(Product.status == status)
    if category:
        q = q.filter(Product.category == category)
    return q.order_by(Product.product_code).all()


def get_product(session: Session, product_id: str) -> Product | None:
    return session.get(Product, product_id)


def get_product_by_code(session: Session, code: str) -> Product | None:
    return session.query(Product).filter(Product.product_code == code).first()


def create_product(session: Session, data: dict) -> Product:
    obj = Product(**data)
    session.add(obj)
    session.flush()
    return obj


def update_product(session: Session, product_id: str, data: dict) -> Product | None:
    obj = session.get(Product, product_id)
    if not obj:
        return None
    for k, v in data.items():
        if v is not None:
            setattr(obj, k, v)
    session.flush()
    return obj


def delete_product(session: Session, product_id: str) -> bool:
    obj = session.get(Product, product_id)
    if not obj:
        return False
    session.delete(obj)
    session.flush()
    return True
