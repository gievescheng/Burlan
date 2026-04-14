"""Domain rules for state transitions.

Defines valid statuses and allowed transitions for each entity type.
"""
from __future__ import annotations

MASTER_DATA_STATUSES = {"active", "inactive", "archived"}

ROUTE_STATUSES = {"active", "inactive", "draft", "archived"}

SALES_ORDER_TRANSITIONS: dict[str, set[str]] = {
    "draft":         {"confirmed", "cancelled"},
    "confirmed":     {"in_production", "cancelled"},
    "in_production": {"completed", "cancelled"},
    "completed":     {"closed"},
    "cancelled":     set(),
    "closed":        set(),
}

WORK_ORDER_TRANSITIONS: dict[str, set[str]] = {
    "draft":       {"released", "cancelled"},
    "released":    {"in_progress", "cancelled"},
    "in_progress": {"completed", "on_hold", "cancelled"},
    "on_hold":     {"in_progress", "cancelled"},
    "completed":   {"closed"},
    "cancelled":   set(),
    "closed":      set(),
}

PRODUCTION_PLAN_TRANSITIONS: dict[str, set[str]] = {
    "draft":       {"approved", "cancelled"},
    "approved":    {"in_progress", "cancelled"},
    "in_progress": {"completed", "on_hold", "cancelled"},
    "on_hold":     {"in_progress", "cancelled"},
    "completed":   {"closed"},
    "cancelled":   set(),
    "closed":      set(),
}

MATERIAL_ISSUE_TRANSITIONS: dict[str, set[str]] = {
    "draft":     {"approved", "cancelled"},
    "approved":  {"issued", "cancelled"},
    "issued":    {"completed"},
    "completed": set(),
    "cancelled": set(),
}

# 檢驗批 — ISO 9001:2015 §8.6 產品放行
INSPECTION_LOT_TRANSITIONS: dict[str, set[str]] = {
    "pending":     {"in_progress", "cancelled"},
    "in_progress": {"passed", "failed", "conditional", "cancelled"},
    "passed":      {"closed"},
    "failed":      {"closed", "in_progress"},          # 重檢
    "conditional": {"passed", "failed", "closed"},     # 待審後決議
    "closed":      set(),
    "cancelled":   set(),
}

# NCR — ISO 9001:2015 §8.7 不合格品輸出管制
NCR_TRANSITIONS: dict[str, set[str]] = {
    "open":                 {"under_review", "disposition_decided", "cancelled"},
    "under_review":         {"disposition_decided", "cancelled"},
    "disposition_decided":  {"in_action", "closed", "cancelled"},
    "in_action":            {"closed", "cancelled"},
    "closed":               set(),
    "cancelled":            set(),
}

# Rework Order — 重工單流程
REWORK_ORDER_TRANSITIONS: dict[str, set[str]] = {
    "planned":     {"in_progress", "cancelled"},
    "in_progress": {"completed", "cancelled"},
    "completed":   set(),
    "cancelled":   set(),
}

# 客訴 — ISO 9001:2015 §9.1.2 顧客滿意度
CUSTOMER_COMPLAINT_TRANSITIONS: dict[str, set[str]] = {
    "received":            {"under_investigation", "responding", "cancelled"},
    "under_investigation": {"responding", "resolved", "cancelled"},
    "responding":          {"resolved", "cancelled"},
    "resolved":            {"closed", "responding"},  # 顧客若不滿可退回再答覆
    "closed":              set(),
    "cancelled":           set(),
}

# CAPA — ISO 9001:2015 §10.2 矯正措施
CAPA_TRANSITIONS: dict[str, set[str]] = {
    "open":        {"in_progress", "cancelled"},
    "in_progress": {"verifying", "cancelled"},
    "verifying":   {"closed", "in_progress", "cancelled"},  # 有效性不足可退回
    "closed":      set(),
    "cancelled":   set(),
}

# 內部稽核 — ISO 9001:2015 §9.2
INTERNAL_AUDIT_TRANSITIONS: dict[str, set[str]] = {
    "planned":     {"in_progress", "cancelled"},
    "in_progress": {"reporting", "cancelled"},
    "reporting":   {"closed", "in_progress", "cancelled"},  # 報告補件可退回
    "closed":      set(),
    "cancelled":   set(),
}

# 稽核發現 — ISO 9001:2015 §9.2.2 e) 發現須追蹤至關閉
AUDIT_FINDING_TRANSITIONS: dict[str, set[str]] = {
    "open":              {"corrective_action", "cancelled"},
    "corrective_action": {"verified", "open", "cancelled"},  # 改善不足可退回
    "verified":          {"closed", "corrective_action"},
    "closed":            set(),
    "cancelled":         set(),
}

# 管理階層審查 — ISO 9001:2015 §9.3
MANAGEMENT_REVIEW_TRANSITIONS: dict[str, set[str]] = {
    "planned":     {"in_progress", "cancelled"},
    "in_progress": {"closed", "cancelled"},
    "closed":      set(),
    "cancelled":   set(),
}

# 管理審查行動項目 — §9.3.3 輸出決議追蹤
REVIEW_ACTION_TRANSITIONS: dict[str, set[str]] = {
    "open":        {"in_progress", "cancelled"},
    "in_progress": {"completed", "cancelled"},
    "completed":   set(),
    "cancelled":   set(),
}

# 設備 — ISO 9001:2015 §7.1.5.2 b) 保存識別狀態
EQUIPMENT_TRANSITIONS: dict[str, set[str]] = {
    "active":  {"hold", "repair", "retired"},
    "hold":    {"active", "repair", "retired"},
    "repair":  {"active", "hold", "retired"},
    "retired": set(),  # 報廢為終態
}

# 校正紀錄 — ISO 9001:2015 §7.1.5.2 a)-d)
CALIBRATION_RECORD_TRANSITIONS: dict[str, set[str]] = {
    "planned":     {"in_progress", "cancelled"},
    "in_progress": {"completed", "cancelled"},
    "completed":   {"verified", "in_progress", "cancelled"},  # 驗證不過可退回
    "verified":    set(),
    "cancelled":   set(),
}

# 預防保養紀錄
PM_RECORD_TRANSITIONS: dict[str, set[str]] = {
    "planned":     {"in_progress", "cancelled"},
    "in_progress": {"completed", "cancelled"},
    "completed":   set(),
    "cancelled":   set(),
}

# 文件版本 — ISO 9001:2015 §7.5.2 審查核准 / §7.5.3 發行與廢止
DOCUMENT_REVISION_TRANSITIONS: dict[str, set[str]] = {
    "draft":        {"under_review", "cancelled"},
    "under_review": {"approved", "draft", "cancelled"},  # 審查未過可退回草稿
    "approved":     {"effective", "cancelled"},
    "effective":    {"superseded", "obsolete"},
    "superseded":   {"obsolete"},  # 被新版本取代 → 最終廢止
    "obsolete":     set(),
    "cancelled":    set(),
}


def validate_status_transition(
    entity_type: str,
    current: str,
    target: str,
) -> str | None:
    """Return an error message if the transition is invalid, else None."""
    _TRANSITION_MAP = {
        "sales_order": SALES_ORDER_TRANSITIONS,
        "work_order": WORK_ORDER_TRANSITIONS,
        "production_plan": PRODUCTION_PLAN_TRANSITIONS,
        "material_issue": MATERIAL_ISSUE_TRANSITIONS,
        "inspection_lot": INSPECTION_LOT_TRANSITIONS,
        "ncr": NCR_TRANSITIONS,
        "rework_order": REWORK_ORDER_TRANSITIONS,
        "customer_complaint": CUSTOMER_COMPLAINT_TRANSITIONS,
        "capa": CAPA_TRANSITIONS,
        "document_revision": DOCUMENT_REVISION_TRANSITIONS,
        "internal_audit": INTERNAL_AUDIT_TRANSITIONS,
        "audit_finding": AUDIT_FINDING_TRANSITIONS,
        "management_review": MANAGEMENT_REVIEW_TRANSITIONS,
        "review_action": REVIEW_ACTION_TRANSITIONS,
        "equipment": EQUIPMENT_TRANSITIONS,
        "calibration_record": CALIBRATION_RECORD_TRANSITIONS,
        "pm_record": PM_RECORD_TRANSITIONS,
    }

    if entity_type in _TRANSITION_MAP:
        transitions = _TRANSITION_MAP[entity_type]
    elif entity_type in ("route", "station"):
        allowed = ROUTE_STATUSES
        if target not in allowed:
            return f"Invalid status '{target}' for {entity_type}. Allowed: {sorted(allowed)}"
        return None
    else:
        allowed = MASTER_DATA_STATUSES
        if target not in allowed:
            return f"Invalid status '{target}' for {entity_type}. Allowed: {sorted(allowed)}"
        return None

    if current not in transitions:
        return f"Unknown current status '{current}' for {entity_type}"
    if target not in transitions[current]:
        allowed = sorted(transitions[current]) if transitions[current] else "none"
        return f"Cannot transition {entity_type} from '{current}' to '{target}'. Allowed: {allowed}"
    return None
