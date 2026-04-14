from __future__ import annotations

from sqlalchemy.orm import Session

from ..repositories import process as repo


def list_stations(session: Session, status: str | None = None) -> list[dict]:
    rows = repo.list_stations(session, status=status)
    return [_row_to_dict(r) for r in rows]


def get_station(session: Session, station_id: str) -> dict | None:
    row = repo.get_station(session, station_id)
    return _row_to_dict(row) if row else None


def create_station(session: Session, data: dict) -> dict:
    if repo.get_station_by_code(session, data["station_code"]):
        raise ValueError(f"Station code '{data['station_code']}' already exists")
    return _row_to_dict(repo.create_station(session, data))


def update_station(session: Session, station_id: str, data: dict) -> dict | None:
    row = repo.update_station(session, station_id, data)
    return _row_to_dict(row) if row else None


def delete_station(session: Session, station_id: str) -> bool:
    return repo.delete_station(session, station_id)


def list_routes(session: Session, status: str | None = None) -> list[dict]:
    rows = repo.list_routes(session, status=status)
    return [_route_to_dict(r) for r in rows]


def get_route(session: Session, route_id: str) -> dict | None:
    row = repo.get_route(session, route_id)
    return _route_to_dict(row) if row else None


def create_route(session: Session, data: dict) -> dict:
    if repo.get_route_by_code(session, data["route_code"]):
        raise ValueError(f"Route code '{data['route_code']}' already exists")
    steps = data.pop("steps", [])
    route = repo.create_route(session, data, steps=steps)
    return _route_to_dict(route)


def update_route(session: Session, route_id: str, data: dict) -> dict | None:
    steps = data.pop("steps", None)
    route = repo.update_route(session, route_id, data, steps=steps)
    return _route_to_dict(route) if route else None


def delete_route(session: Session, route_id: str) -> bool:
    return repo.delete_route(session, route_id)


def _row_to_dict(row) -> dict:
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}


def _route_to_dict(route) -> dict:
    d = _row_to_dict(route)
    d["steps"] = [_row_to_dict(s) for s in route.steps]
    return d
