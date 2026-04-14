"""Unit tests for ERP-QMS core models and repositories."""
from __future__ import annotations

from erp_qms_core.repositories import master as master_repo
from erp_qms_core.repositories import process as process_repo


class TestCustomerRepository:
    def test_create_and_get(self, db_session):
        c = master_repo.create_customer(db_session, {
            "customer_code": "C001",
            "name": "Test Customer",
        })
        db_session.flush()
        assert c.id
        assert c.customer_code == "C001"

        fetched = master_repo.get_customer(db_session, c.id)
        assert fetched is not None
        assert fetched.name == "Test Customer"

    def test_list_filter_by_status(self, db_session):
        master_repo.create_customer(db_session, {"customer_code": "C001", "name": "A", "status": "active"})
        master_repo.create_customer(db_session, {"customer_code": "C002", "name": "B", "status": "inactive"})
        db_session.flush()

        active = master_repo.list_customers(db_session, status="active")
        assert len(active) == 1
        assert active[0].customer_code == "C001"

    def test_update(self, db_session):
        c = master_repo.create_customer(db_session, {"customer_code": "C001", "name": "Old"})
        db_session.flush()
        updated = master_repo.update_customer(db_session, c.id, {"name": "New"})
        assert updated.name == "New"

    def test_delete(self, db_session):
        c = master_repo.create_customer(db_session, {"customer_code": "C001", "name": "Del"})
        db_session.flush()
        assert master_repo.delete_customer(db_session, c.id) is True
        assert master_repo.get_customer(db_session, c.id) is None

    def test_duplicate_code_rejected(self, db_session):
        master_repo.create_customer(db_session, {"customer_code": "C001", "name": "First"})
        db_session.flush()
        import pytest
        with pytest.raises(Exception):
            master_repo.create_customer(db_session, {"customer_code": "C001", "name": "Second"})
            db_session.flush()


class TestSupplierRepository:
    def test_create_and_get(self, db_session):
        s = master_repo.create_supplier(db_session, {
            "supplier_code": "S001",
            "name": "Test Supplier",
        })
        db_session.flush()
        assert s.supplier_code == "S001"
        assert master_repo.get_supplier_by_code(db_session, "S001") is not None


class TestProductRepository:
    def test_create_and_filter(self, db_session):
        master_repo.create_product(db_session, {"product_code": "P001", "name": "Widget", "category": "A"})
        master_repo.create_product(db_session, {"product_code": "P002", "name": "Gadget", "category": "B"})
        db_session.flush()

        cat_a = master_repo.list_products(db_session, category="A")
        assert len(cat_a) == 1
        assert cat_a[0].product_code == "P001"


class TestProcessStationRepository:
    def test_create_and_get(self, db_session):
        st = process_repo.create_station(db_session, {
            "station_code": "ST01",
            "name": "Cutting",
        })
        db_session.flush()
        assert st.station_code == "ST01"
        assert process_repo.get_station_by_code(db_session, "ST01") is not None


class TestProcessRouteRepository:
    def test_create_route_with_steps(self, db_session):
        st1 = process_repo.create_station(db_session, {"station_code": "ST01", "name": "Cut"})
        st2 = process_repo.create_station(db_session, {"station_code": "ST02", "name": "Polish"})
        db_session.flush()

        route = process_repo.create_route(
            db_session,
            {"route_code": "R001", "name": "Standard Route"},
            steps=[
                {"station_id": st1.id, "seq": 1, "standard_time_min": 10.0},
                {"station_id": st2.id, "seq": 2, "standard_time_min": 15.0},
            ],
        )
        db_session.flush()
        assert route.route_code == "R001"
        assert len(route.steps) == 2
        assert route.steps[0].seq == 1
        assert route.steps[1].seq == 2

    def test_update_route_replaces_steps(self, db_session):
        st1 = process_repo.create_station(db_session, {"station_code": "ST01", "name": "Cut"})
        st2 = process_repo.create_station(db_session, {"station_code": "ST02", "name": "Polish"})
        db_session.flush()

        route = process_repo.create_route(
            db_session,
            {"route_code": "R001", "name": "Route"},
            steps=[{"station_id": st1.id, "seq": 1}],
        )
        db_session.flush()

        updated = process_repo.update_route(
            db_session, route.id, {"name": "Updated Route"},
            steps=[{"station_id": st2.id, "seq": 1}],
        )
        db_session.flush()
        assert updated.name == "Updated Route"
        assert len(updated.steps) == 1
        assert updated.steps[0].station_id == st2.id

    def test_delete_route_cascades(self, db_session):
        st = process_repo.create_station(db_session, {"station_code": "ST01", "name": "Cut"})
        db_session.flush()
        route = process_repo.create_route(
            db_session,
            {"route_code": "R001", "name": "Route"},
            steps=[{"station_id": st.id, "seq": 1}],
        )
        db_session.flush()
        assert process_repo.delete_route(db_session, route.id) is True
        assert process_repo.get_route(db_session, route.id) is None
