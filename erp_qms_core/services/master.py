from __future__ import annotations

from sqlalchemy.orm import Session

from ..repositories import master as repo


def list_customers(session: Session, status: str | None = None) -> list[dict]:
    rows = repo.list_customers(session, status=status)
    return [_row_to_dict(r) for r in rows]


def get_customer(session: Session, customer_id: str) -> dict | None:
    row = repo.get_customer(session, customer_id)
    return _row_to_dict(row) if row else None


def create_customer(session: Session, data: dict) -> dict:
    if repo.get_customer_by_code(session, data["customer_code"]):
        raise ValueError(f"Customer code '{data['customer_code']}' already exists")
    return _row_to_dict(repo.create_customer(session, data))


def update_customer(session: Session, customer_id: str, data: dict) -> dict | None:
    row = repo.update_customer(session, customer_id, data)
    return _row_to_dict(row) if row else None


def delete_customer(session: Session, customer_id: str) -> bool:
    return repo.delete_customer(session, customer_id)


def list_suppliers(session: Session, status: str | None = None) -> list[dict]:
    rows = repo.list_suppliers(session, status=status)
    return [_row_to_dict(r) for r in rows]


def get_supplier(session: Session, supplier_id: str) -> dict | None:
    row = repo.get_supplier(session, supplier_id)
    return _row_to_dict(row) if row else None


def create_supplier(session: Session, data: dict) -> dict:
    if repo.get_supplier_by_code(session, data["supplier_code"]):
        raise ValueError(f"Supplier code '{data['supplier_code']}' already exists")
    return _row_to_dict(repo.create_supplier(session, data))


def update_supplier(session: Session, supplier_id: str, data: dict) -> dict | None:
    row = repo.update_supplier(session, supplier_id, data)
    return _row_to_dict(row) if row else None


def delete_supplier(session: Session, supplier_id: str) -> bool:
    return repo.delete_supplier(session, supplier_id)


def list_products(session: Session, status: str | None = None, category: str | None = None) -> list[dict]:
    rows = repo.list_products(session, status=status, category=category)
    return [_row_to_dict(r) for r in rows]


def get_product(session: Session, product_id: str) -> dict | None:
    row = repo.get_product(session, product_id)
    return _row_to_dict(row) if row else None


def create_product(session: Session, data: dict) -> dict:
    if repo.get_product_by_code(session, data["product_code"]):
        raise ValueError(f"Product code '{data['product_code']}' already exists")
    return _row_to_dict(repo.create_product(session, data))


def update_product(session: Session, product_id: str, data: dict) -> dict | None:
    row = repo.update_product(session, product_id, data)
    return _row_to_dict(row) if row else None


def delete_product(session: Session, product_id: str) -> bool:
    return repo.delete_product(session, product_id)


def _row_to_dict(row) -> dict:
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}
