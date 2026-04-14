from __future__ import annotations

from sqlalchemy.orm import Session

from ..models.process import ProcessRoute, ProcessRouteStep, ProcessStation


# ── ProcessStation ──────────────────────────────────────

def list_stations(session: Session, *, status: str | None = None) -> list[ProcessStation]:
    q = session.query(ProcessStation)
    if status:
        q = q.filter(ProcessStation.status == status)
    return q.order_by(ProcessStation.station_code).all()


def get_station(session: Session, station_id: str) -> ProcessStation | None:
    return session.get(ProcessStation, station_id)


def get_station_by_code(session: Session, code: str) -> ProcessStation | None:
    return session.query(ProcessStation).filter(ProcessStation.station_code == code).first()


def create_station(session: Session, data: dict) -> ProcessStation:
    obj = ProcessStation(**data)
    session.add(obj)
    session.flush()
    return obj


def update_station(session: Session, station_id: str, data: dict) -> ProcessStation | None:
    obj = session.get(ProcessStation, station_id)
    if not obj:
        return None
    for k, v in data.items():
        if v is not None:
            setattr(obj, k, v)
    session.flush()
    return obj


def delete_station(session: Session, station_id: str) -> bool:
    obj = session.get(ProcessStation, station_id)
    if not obj:
        return False
    session.delete(obj)
    session.flush()
    return True


# ── ProcessRoute ────────────────────────────────────────

def list_routes(session: Session, *, status: str | None = None) -> list[ProcessRoute]:
    q = session.query(ProcessRoute)
    if status:
        q = q.filter(ProcessRoute.status == status)
    return q.order_by(ProcessRoute.route_code).all()


def get_route(session: Session, route_id: str) -> ProcessRoute | None:
    return session.get(ProcessRoute, route_id)


def get_route_by_code(session: Session, code: str) -> ProcessRoute | None:
    return session.query(ProcessRoute).filter(ProcessRoute.route_code == code).first()


def create_route(session: Session, data: dict, steps: list[dict] | None = None) -> ProcessRoute:
    route = ProcessRoute(**data)
    session.add(route)
    session.flush()
    if steps:
        for step_data in steps:
            step = ProcessRouteStep(route_id=route.id, **step_data)
            session.add(step)
        session.flush()
    return route


def update_route(session: Session, route_id: str, data: dict, steps: list[dict] | None = None) -> ProcessRoute | None:
    route = session.get(ProcessRoute, route_id)
    if not route:
        return None
    for k, v in data.items():
        if v is not None:
            setattr(route, k, v)
    if steps is not None:
        for old_step in list(route.steps):
            session.delete(old_step)
        session.flush()
        for step_data in steps:
            step = ProcessRouteStep(route_id=route.id, **step_data)
            session.add(step)
        session.flush()
        session.expire(route, ["steps"])
    session.flush()
    return route


def delete_route(session: Session, route_id: str) -> bool:
    route = session.get(ProcessRoute, route_id)
    if not route:
        return False
    session.delete(route)
    session.flush()
    return True
