from __future__ import annotations

from sqlalchemy.orm import Session

from ..models.logging import ProcessParamCheck, ProductionLog


def list_production_logs(
    session: Session,
    *,
    status: str | None = None,
    work_order_id: str | None = None,
    station_id: str | None = None,
    lot_no: str | None = None,
) -> list[ProductionLog]:
    q = session.query(ProductionLog)
    if status:
        q = q.filter(ProductionLog.status == status)
    if work_order_id:
        q = q.filter(ProductionLog.work_order_id == work_order_id)
    if station_id:
        q = q.filter(ProductionLog.station_id == station_id)
    if lot_no:
        q = q.filter(ProductionLog.lot_no == lot_no)
    return q.order_by(ProductionLog.log_no.desc()).all()


def get_production_log(session: Session, log_id: str) -> ProductionLog | None:
    return session.get(ProductionLog, log_id)


def get_production_log_by_no(session: Session, log_no: str) -> ProductionLog | None:
    return session.query(ProductionLog).filter(ProductionLog.log_no == log_no).first()


def create_production_log(session: Session, data: dict, param_checks: list[dict] | None = None) -> ProductionLog:
    log = ProductionLog(**data)
    session.add(log)
    session.flush()
    if param_checks:
        for pc in param_checks:
            pc_obj = ProcessParamCheck(production_log_id=log.id, **pc)
            _auto_judge(pc_obj)
            session.add(pc_obj)
        session.flush()
    return log


def update_production_log(
    session: Session, log_id: str, data: dict, param_checks: list[dict] | None = None,
) -> ProductionLog | None:
    log = session.get(ProductionLog, log_id)
    if not log:
        return None
    for k, v in data.items():
        if v is not None:
            setattr(log, k, v)
    if param_checks is not None:
        for old in list(log.param_checks):
            session.delete(old)
        session.flush()
        for pc in param_checks:
            pc_obj = ProcessParamCheck(production_log_id=log.id, **pc)
            _auto_judge(pc_obj)
            session.add(pc_obj)
        session.flush()
        session.expire(log, ["param_checks"])
    session.flush()
    return log


def delete_production_log(session: Session, log_id: str) -> bool:
    log = session.get(ProductionLog, log_id)
    if not log:
        return False
    session.delete(log)
    session.flush()
    return True


def _auto_judge(pc: ProcessParamCheck) -> None:
    """根據 LSL/USL 自動判定 pass/fail（若未明確指定 result）。"""
    if pc.result and pc.result != "pass":
        return
    if pc.lsl is not None and pc.param_value < pc.lsl:
        pc.result = "fail"
    elif pc.usl is not None and pc.param_value > pc.usl:
        pc.result = "fail"
    else:
        pc.result = "pass"
