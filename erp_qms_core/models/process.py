from __future__ import annotations

from sqlalchemy import Float, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .base import AuditMixin, new_id


class ProcessStation(AuditMixin, Base):
    """製程站點"""
    __tablename__ = "erp_process_stations"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=new_id)
    station_code: Mapped[str] = mapped_column(Text, unique=True, index=True)
    name: Mapped[str] = mapped_column(Text, index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    department: Mapped[str] = mapped_column(Text, default="")
    station_type: Mapped[str] = mapped_column(Text, default="production")
    capacity_per_hour: Mapped[float] = mapped_column(Float, default=0.0)
    requires_inspection: Mapped[str] = mapped_column(Text, default="no")
    status: Mapped[str] = mapped_column(Text, default="active", index=True)
    notes: Mapped[str] = mapped_column(Text, default="")


class ProcessRoute(AuditMixin, Base):
    """製程路線"""
    __tablename__ = "erp_process_routes"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=new_id)
    route_code: Mapped[str] = mapped_column(Text, unique=True, index=True)
    name: Mapped[str] = mapped_column(Text, index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    version: Mapped[str] = mapped_column(Text, default="1.0")
    status: Mapped[str] = mapped_column(Text, default="active", index=True)
    notes: Mapped[str] = mapped_column(Text, default="")

    steps: Mapped[list[ProcessRouteStep]] = relationship(
        back_populates="route",
        cascade="all, delete-orphan",
        order_by="ProcessRouteStep.seq",
    )


class ProcessRouteStep(AuditMixin, Base):
    """製程路線步驟 — 將站點按順序串成路線"""
    __tablename__ = "erp_process_route_steps"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=new_id)
    route_id: Mapped[str] = mapped_column(
        ForeignKey("erp_process_routes.id", ondelete="CASCADE"), index=True,
    )
    station_id: Mapped[str] = mapped_column(
        ForeignKey("erp_process_stations.id"), index=True,
    )
    seq: Mapped[int] = mapped_column(Integer)
    standard_time_min: Mapped[float] = mapped_column(Float, default=0.0)
    setup_time_min: Mapped[float] = mapped_column(Float, default=0.0)
    is_optional: Mapped[str] = mapped_column(Text, default="no")
    notes: Mapped[str] = mapped_column(Text, default="")

    route: Mapped[ProcessRoute] = relationship(back_populates="steps")

    __table_args__ = (
        UniqueConstraint("route_id", "seq", name="uq_route_step_seq"),
    )
