from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .. import database
from ..schemas.process import (
    ProcessRouteCreate, ProcessRouteOut, ProcessRouteUpdate,
    ProcessStationCreate, ProcessStationOut, ProcessStationUpdate,
)
from ..services import process as svc

router = APIRouter()


# ── ProcessStation ──────────────────────────────────────

@router.get("/stations", response_model=list[ProcessStationOut])
def list_stations(status: str | None = None):
    with database.session_scope() as s:
        return svc.list_stations(s, status=status)


@router.get("/stations/{station_id}", response_model=ProcessStationOut)
def get_station(station_id: str):
    with database.session_scope() as s:
        row = svc.get_station(s, station_id)
    if not row:
        raise HTTPException(404, "Station not found")
    return row


@router.post("/stations", response_model=ProcessStationOut, status_code=201)
def create_station(body: ProcessStationCreate):
    try:
        with database.session_scope() as s:
            return svc.create_station(s, body.model_dump())
    except ValueError as e:
        raise HTTPException(409, str(e))


@router.patch("/stations/{station_id}", response_model=ProcessStationOut)
def update_station(station_id: str, body: ProcessStationUpdate):
    with database.session_scope() as s:
        row = svc.update_station(s, station_id, body.model_dump(exclude_unset=True))
    if not row:
        raise HTTPException(404, "Station not found")
    return row


@router.delete("/stations/{station_id}", status_code=204)
def delete_station(station_id: str):
    with database.session_scope() as s:
        if not svc.delete_station(s, station_id):
            raise HTTPException(404, "Station not found")


# ── ProcessRoute ────────────────────────────────────────

@router.get("/routes", response_model=list[ProcessRouteOut])
def list_routes(status: str | None = None):
    with database.session_scope() as s:
        return svc.list_routes(s, status=status)


@router.get("/routes/{route_id}", response_model=ProcessRouteOut)
def get_route(route_id: str):
    with database.session_scope() as s:
        row = svc.get_route(s, route_id)
    if not row:
        raise HTTPException(404, "Route not found")
    return row


@router.post("/routes", response_model=ProcessRouteOut, status_code=201)
def create_route(body: ProcessRouteCreate):
    try:
        with database.session_scope() as s:
            return svc.create_route(s, body.model_dump())
    except ValueError as e:
        raise HTTPException(409, str(e))


@router.patch("/routes/{route_id}", response_model=ProcessRouteOut)
def update_route(route_id: str, body: ProcessRouteUpdate):
    with database.session_scope() as s:
        row = svc.update_route(s, route_id, body.model_dump(exclude_unset=True))
    if not row:
        raise HTTPException(404, "Route not found")
    return row


@router.delete("/routes/{route_id}", status_code=204)
def delete_route(route_id: str):
    with database.session_scope() as s:
        if not svc.delete_route(s, route_id):
            raise HTTPException(404, "Route not found")
