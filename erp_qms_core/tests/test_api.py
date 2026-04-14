"""Integration tests for ERP-QMS core API endpoints."""
from __future__ import annotations


class TestCustomerAPI:
    def test_crud_lifecycle(self, client):
        # Create
        resp = client.post("/api/erp/customers", json={
            "customer_code": "C001",
            "name": "Acme Corp",
            "phone": "02-1234-5678",
        })
        assert resp.status_code == 201
        data = resp.json()
        cid = data["id"]
        assert data["customer_code"] == "C001"
        assert data["name"] == "Acme Corp"
        assert data["status"] == "active"

        # Read
        resp = client.get(f"/api/erp/customers/{cid}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Acme Corp"

        # List
        resp = client.get("/api/erp/customers")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

        # Update
        resp = client.patch(f"/api/erp/customers/{cid}", json={"name": "Acme Inc"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "Acme Inc"

        # Delete
        resp = client.delete(f"/api/erp/customers/{cid}")
        assert resp.status_code == 204

        # Confirm deleted
        resp = client.get(f"/api/erp/customers/{cid}")
        assert resp.status_code == 404

    def test_duplicate_code_returns_409(self, client):
        client.post("/api/erp/customers", json={"customer_code": "C001", "name": "A"})
        resp = client.post("/api/erp/customers", json={"customer_code": "C001", "name": "B"})
        assert resp.status_code == 409


class TestSupplierAPI:
    def test_create_and_list(self, client):
        resp = client.post("/api/erp/suppliers", json={
            "supplier_code": "S001",
            "name": "Parts Co",
        })
        assert resp.status_code == 201

        resp = client.get("/api/erp/suppliers")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1


class TestProductAPI:
    def test_create_and_filter_by_category(self, client):
        client.post("/api/erp/products", json={"product_code": "P001", "name": "Widget", "category": "optical"})
        client.post("/api/erp/products", json={"product_code": "P002", "name": "Gadget", "category": "lens"})

        resp = client.get("/api/erp/products?category=optical")
        assert resp.status_code == 200
        items = resp.json()
        assert len(items) == 1
        assert items[0]["product_code"] == "P001"


class TestStationAPI:
    def test_crud(self, client):
        resp = client.post("/api/erp/stations", json={
            "station_code": "ST01",
            "name": "Cutting",
            "department": "Manufacturing",
        })
        assert resp.status_code == 201
        sid = resp.json()["id"]

        resp = client.patch(f"/api/erp/stations/{sid}", json={"name": "Precision Cutting"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "Precision Cutting"

        resp = client.delete(f"/api/erp/stations/{sid}")
        assert resp.status_code == 204


class TestRouteAPI:
    def test_create_route_with_steps(self, client):
        # Create stations first
        r1 = client.post("/api/erp/stations", json={"station_code": "ST01", "name": "Cut"})
        r2 = client.post("/api/erp/stations", json={"station_code": "ST02", "name": "Polish"})
        st1_id = r1.json()["id"]
        st2_id = r2.json()["id"]

        # Create route with steps
        resp = client.post("/api/erp/routes", json={
            "route_code": "R001",
            "name": "Standard Process",
            "steps": [
                {"station_id": st1_id, "seq": 1, "standard_time_min": 10.0},
                {"station_id": st2_id, "seq": 2, "standard_time_min": 15.0},
            ],
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["route_code"] == "R001"
        assert len(data["steps"]) == 2

    def test_update_route_steps(self, client):
        r1 = client.post("/api/erp/stations", json={"station_code": "ST01", "name": "Cut"})
        r2 = client.post("/api/erp/stations", json={"station_code": "ST02", "name": "Polish"})
        st1_id = r1.json()["id"]
        st2_id = r2.json()["id"]

        resp = client.post("/api/erp/routes", json={
            "route_code": "R001",
            "name": "Route",
            "steps": [{"station_id": st1_id, "seq": 1}],
        })
        route_id = resp.json()["id"]

        resp = client.patch(f"/api/erp/routes/{route_id}", json={
            "steps": [
                {"station_id": st2_id, "seq": 1, "standard_time_min": 20.0},
            ],
        })
        assert resp.status_code == 200
        assert len(resp.json()["steps"]) == 1
        assert resp.json()["steps"][0]["station_id"] == st2_id
