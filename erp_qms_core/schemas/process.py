from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


# ── ProcessStation ──────────────────────────────────────

class ProcessStationCreate(BaseModel):
    station_code: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    description: str = ""
    department: str = ""
    station_type: str = "production"
    capacity_per_hour: float = 0.0
    requires_inspection: str = "no"
    notes: str = ""


class ProcessStationUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    department: str | None = None
    station_type: str | None = None
    capacity_per_hour: float | None = None
    requires_inspection: str | None = None
    status: str | None = None
    notes: str | None = None


class ProcessStationOut(BaseModel):
    id: str
    station_code: str
    name: str
    description: str
    department: str
    station_type: str
    capacity_per_hour: float
    requires_inspection: str
    status: str
    notes: str
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── ProcessRoute ────────────────────────────────────────

class RouteStepInput(BaseModel):
    station_id: str = Field(..., min_length=1)
    seq: int = Field(..., ge=1)
    standard_time_min: float = 0.0
    setup_time_min: float = 0.0
    is_optional: str = "no"
    notes: str = ""


class ProcessRouteCreate(BaseModel):
    route_code: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    description: str = ""
    version: str = "1.0"
    steps: list[RouteStepInput] = []
    notes: str = ""


class ProcessRouteUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    version: str | None = None
    status: str | None = None
    steps: list[RouteStepInput] | None = None
    notes: str | None = None


class RouteStepOut(BaseModel):
    id: str
    route_id: str
    station_id: str
    seq: int
    standard_time_min: float
    setup_time_min: float
    is_optional: str
    notes: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProcessRouteOut(BaseModel):
    id: str
    route_code: str
    name: str
    description: str
    version: str
    status: str
    notes: str
    steps: list[RouteStepOut] = []
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
