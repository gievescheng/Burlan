"""Tests for Equipment / Calibration / Preventive Maintenance (ISO 9001:2015 §7.1.5)."""
from __future__ import annotations

from datetime import date

from erp_qms_core.domain.transitions import validate_status_transition
from erp_qms_core.repositories import equipment as equipment_repo


# ── Domain transitions ─────────────────────────────────

class TestEquipmentTransitions:
    def test_active_to_hold(self):
        assert validate_status_transition(
            "equipment", "active", "hold",
        ) is None

    def test_hold_to_active(self):
        assert validate_status_transition(
            "equipment", "hold", "active",
        ) is None

    def test_repair_to_active(self):
        assert validate_status_transition(
            "equipment", "repair", "active",
        ) is None

    def test_retired_is_terminal(self):
        err = validate_status_transition(
            "equipment", "retired", "active",
        )
        assert err is not None


class TestCalibrationTransitions:
    def test_planned_to_in_progress(self):
        assert validate_status_transition(
            "calibration_record", "planned", "in_progress",
        ) is None

    def test_completed_to_verified(self):
        assert validate_status_transition(
            "calibration_record", "completed", "verified",
        ) is None

    def test_completed_can_reopen(self):
        """驗證不過可退回 in_progress"""
        assert validate_status_transition(
            "calibration_record", "completed", "in_progress",
        ) is None

    def test_verified_is_terminal(self):
        err = validate_status_transition(
            "calibration_record", "verified", "completed",
        )
        assert err is not None

    def test_skip_to_verified_blocked(self):
        err = validate_status_transition(
            "calibration_record", "planned", "verified",
        )
        assert err is not None


class TestPMRecordTransitions:
    def test_planned_to_in_progress(self):
        assert validate_status_transition(
            "pm_record", "planned", "in_progress",
        ) is None

    def test_in_progress_to_completed(self):
        assert validate_status_transition(
            "pm_record", "in_progress", "completed",
        ) is None

    def test_completed_is_terminal(self):
        err = validate_status_transition(
            "pm_record", "completed", "in_progress",
        )
        assert err is not None


# ── Equipment Repository ───────────────────────────────

class TestEquipmentRepository:
    def test_create_equipment(self, db_session):
        e = equipment_repo.create_equipment(db_session, {
            "equipment_no": "CAL-001",
            "name": "Digital Caliper",
            "equipment_type": "measurement",
            "requires_calibration": True,
            "calibration_interval_months": 12,
        })
        db_session.flush()
        assert e.equipment_no == "CAL-001"
        assert e.status == "active"
        assert e.requires_calibration is True

    def test_filter_by_requires_calibration(self, db_session):
        equipment_repo.create_equipment(db_session, {
            "equipment_no": "C1", "requires_calibration": True,
        })
        equipment_repo.create_equipment(db_session, {
            "equipment_no": "P1", "requires_calibration": False,
        })
        db_session.flush()
        cal_items = equipment_repo.list_equipments(
            db_session, requires_calibration=True,
        )
        assert len(cal_items) == 1
        assert cal_items[0].equipment_no == "C1"


# ── Equipment API ──────────────────────────────────────

class TestEquipmentAPI:
    def test_create_equipment(self, client):
        r = client.post("/api/erp/equipments", json={
            "equipment_no": "EQ-API-01",
            "name": "Vernier Caliper 0-150mm",
            "equipment_type": "measurement",
            "requires_calibration": True,
            "calibration_interval_months": 12,
        })
        assert r.status_code == 201
        assert r.json()["equipment_no"] == "EQ-API-01"
        assert r.json()["status"] == "active"

    def test_invalid_equipment_type_422(self, client):
        r = client.post("/api/erp/equipments", json={
            "equipment_no": "EQ-BAD", "equipment_type": "unknown",
        })
        assert r.status_code == 422

    def test_duplicate_equipment_no_409(self, client):
        client.post("/api/erp/equipments", json={"equipment_no": "EQ-DUP"})
        r = client.post("/api/erp/equipments", json={"equipment_no": "EQ-DUP"})
        assert r.status_code == 409

    def test_requires_calibration_needs_interval(self, client):
        """ISO §7.1.5.2 — 需校正設備必須有週期"""
        r = client.post("/api/erp/equipments", json={
            "equipment_no": "EQ-NOINT",
            "requires_calibration": True,
            "calibration_interval_months": 0,
        })
        assert r.status_code == 422
        assert "interval" in r.text.lower()

    def test_requires_pm_needs_interval(self, client):
        r = client.post("/api/erp/equipments", json={
            "equipment_no": "EQ-NOPM",
            "requires_pm": True,
            "pm_interval_days": 0,
        })
        assert r.status_code == 422

    def test_equipment_lifecycle(self, client):
        e = client.post("/api/erp/equipments", json={
            "equipment_no": "EQ-LIFE",
        }).json()
        # active → hold
        r = client.patch(f"/api/erp/equipments/{e['id']}", json={
            "status": "hold", "hold_reason": "pending calibration",
        })
        assert r.status_code == 200
        assert r.json()["status"] == "hold"
        # hold → active
        r = client.patch(f"/api/erp/equipments/{e['id']}", json={
            "status": "active",
        })
        assert r.status_code == 200

    def test_invalid_status_transition_422(self, client):
        e = client.post("/api/erp/equipments", json={
            "equipment_no": "EQ-RETIRED",
        }).json()
        client.patch(f"/api/erp/equipments/{e['id']}",
                     json={"status": "retired"})
        r = client.patch(f"/api/erp/equipments/{e['id']}",
                         json={"status": "active"})
        assert r.status_code == 422


# ── Calibration API ────────────────────────────────────

class TestCalibrationAPI:
    def _make_equipment(self, client, no="EQ-C", requires_cal=True):
        return client.post("/api/erp/equipments", json={
            "equipment_no": no,
            "requires_calibration": requires_cal,
            "calibration_interval_months": 12 if requires_cal else 0,
        }).json()

    def test_create_calibration(self, client):
        eq = self._make_equipment(client)
        r = client.post("/api/erp/calibrations", json={
            "calibration_no": "CAL-001",
            "equipment_id": eq["id"],
            "calibration_type": "external",
            "calibration_date": "2026-01-15",
            "vendor": "TAF Lab",
        })
        assert r.status_code == 201
        assert r.json()["calibration_no"] == "CAL-001"
        assert r.json()["status"] == "planned"

    def test_invalid_calibration_type_422(self, client):
        eq = self._make_equipment(client, "EQ-CT")
        r = client.post("/api/erp/calibrations", json={
            "calibration_no": "CAL-BAD",
            "equipment_id": eq["id"],
            "calibration_type": "magical",
        })
        assert r.status_code == 422

    def test_calibration_for_missing_equipment(self, client):
        r = client.post("/api/erp/calibrations", json={
            "calibration_no": "CAL-ORPH",
            "equipment_id": "nonexistent",
        })
        assert r.status_code == 422

    def test_duplicate_calibration_no_409(self, client):
        eq = self._make_equipment(client, "EQ-DUP2")
        client.post("/api/erp/calibrations", json={
            "calibration_no": "CAL-DUP", "equipment_id": eq["id"],
        })
        r = client.post("/api/erp/calibrations", json={
            "calibration_no": "CAL-DUP", "equipment_id": eq["id"],
        })
        assert r.status_code == 409

    def test_cannot_verify_without_result(self, client):
        """ISO §7.1.5.2 — verified 必須有結果"""
        eq = self._make_equipment(client, "EQ-VR")
        cal = client.post("/api/erp/calibrations", json={
            "calibration_no": "CAL-VR", "equipment_id": eq["id"],
            "calibration_date": "2026-02-01",
        }).json()
        client.patch(f"/api/erp/calibrations/{cal['id']}",
                     json={"status": "in_progress"})
        client.patch(f"/api/erp/calibrations/{cal['id']}",
                     json={"status": "completed"})
        # 跳過結果試圖 verify
        r = client.patch(f"/api/erp/calibrations/{cal['id']}",
                         json={"status": "verified", "verified_by": "QM"})
        assert r.status_code == 422
        assert "result" in r.text.lower()

    def test_cannot_verify_without_verifier(self, client):
        eq = self._make_equipment(client, "EQ-VB")
        cal = client.post("/api/erp/calibrations", json={
            "calibration_no": "CAL-VB", "equipment_id": eq["id"],
            "calibration_date": "2026-02-01",
        }).json()
        client.patch(f"/api/erp/calibrations/{cal['id']}",
                     json={"status": "in_progress"})
        client.patch(f"/api/erp/calibrations/{cal['id']}",
                     json={"status": "completed", "result": "passed"})
        r = client.patch(f"/api/erp/calibrations/{cal['id']}",
                         json={"status": "verified"})
        assert r.status_code == 422
        assert "verified_by" in r.text

    def test_passed_calibration_updates_equipment(self, client):
        """ISO §7.1.5.2 — 通過校正更新 last_calibration_date/next_calibration_due"""
        eq = self._make_equipment(client, "EQ-PASS")
        cal = client.post("/api/erp/calibrations", json={
            "calibration_no": "CAL-PASS",
            "equipment_id": eq["id"],
            "calibration_date": "2026-01-15",
        }).json()
        client.patch(f"/api/erp/calibrations/{cal['id']}",
                     json={"status": "in_progress"})
        client.patch(f"/api/erp/calibrations/{cal['id']}", json={
            "status": "completed",
            "result": "passed",
        })
        r = client.patch(f"/api/erp/calibrations/{cal['id']}", json={
            "status": "verified", "verified_by": "QM",
        })
        assert r.status_code == 200
        # 驗證設備主檔被更新
        eq2 = client.get(f"/api/erp/equipments/{eq['id']}").json()
        assert eq2["last_calibration_date"] == "2026-01-15"
        assert eq2["next_calibration_due"] == "2027-01-15"

    def test_failed_calibration_puts_equipment_on_hold(self, client):
        """ISO §7.1.5.2 b)-c) — 失效量具自動識別、隔離"""
        eq = self._make_equipment(client, "EQ-FAIL")
        cal = client.post("/api/erp/calibrations", json={
            "calibration_no": "CAL-FAIL",
            "equipment_id": eq["id"],
            "calibration_date": "2026-03-01",
        }).json()
        client.patch(f"/api/erp/calibrations/{cal['id']}",
                     json={"status": "in_progress"})
        client.patch(f"/api/erp/calibrations/{cal['id']}", json={
            "status": "completed",
            "result": "failed",
            "deviation": 0.15,
            "tolerance": 0.05,
            "affected_lots": "LOT-2026-01, LOT-2026-02",
        })
        client.patch(f"/api/erp/calibrations/{cal['id']}", json={
            "status": "verified", "verified_by": "QM",
        })
        eq2 = client.get(f"/api/erp/equipments/{eq['id']}").json()
        assert eq2["status"] == "hold"
        assert "CAL-FAIL" in eq2["hold_reason"]

    def test_filter_calibrations_by_equipment(self, client):
        eq1 = self._make_equipment(client, "EQ-F1")
        eq2 = self._make_equipment(client, "EQ-F2")
        client.post("/api/erp/calibrations", json={
            "calibration_no": "CAL-F1A", "equipment_id": eq1["id"],
        })
        client.post("/api/erp/calibrations", json={
            "calibration_no": "CAL-F1B", "equipment_id": eq1["id"],
        })
        client.post("/api/erp/calibrations", json={
            "calibration_no": "CAL-F2A", "equipment_id": eq2["id"],
        })
        r = client.get(f"/api/erp/calibrations?equipment_id={eq1['id']}")
        assert r.status_code == 200
        assert len(r.json()) == 2


# ── PM Plan + Record API ───────────────────────────────

class TestPMAPI:
    def _make_equipment(self, client, no="EQ-PM"):
        return client.post("/api/erp/equipments", json={
            "equipment_no": no,
            "requires_pm": True,
            "pm_interval_days": 30,
        }).json()

    def test_create_pm_plan(self, client):
        eq = self._make_equipment(client)
        r = client.post("/api/erp/pm-plans", json={
            "plan_no": "PMP-001",
            "equipment_id": eq["id"],
            "plan_type": "monthly",
            "interval_days": 30,
            "tasks": "清潔、潤滑、點檢",
        })
        assert r.status_code == 201

    def test_invalid_plan_type_422(self, client):
        eq = self._make_equipment(client, "EQ-PM-BAD")
        r = client.post("/api/erp/pm-plans", json={
            "plan_no": "PMP-BAD",
            "equipment_id": eq["id"],
            "plan_type": "biennial",
        })
        assert r.status_code == 422

    def test_create_pm_record(self, client):
        eq = self._make_equipment(client, "EQ-PM-R")
        r = client.post("/api/erp/pm-records", json={
            "pm_no": "PMR-001",
            "equipment_id": eq["id"],
            "pm_type": "preventive",
            "scheduled_date": "2026-05-01",
        })
        assert r.status_code == 201
        assert r.json()["status"] == "planned"

    def test_pm_record_for_retired_equipment_blocked(self, client):
        eq = self._make_equipment(client, "EQ-RET")
        client.patch(f"/api/erp/equipments/{eq['id']}",
                     json={"status": "retired"})
        r = client.post("/api/erp/pm-records", json={
            "pm_no": "PMR-RET",
            "equipment_id": eq["id"],
        })
        assert r.status_code == 422
        assert "retired" in r.text.lower()

    def test_complete_pm_updates_equipment(self, client):
        """PM 完成自動更新 last_pm_date / next_pm_due"""
        eq = self._make_equipment(client, "EQ-PM-CMPL")
        pm = client.post("/api/erp/pm-records", json={
            "pm_no": "PMR-CMPL",
            "equipment_id": eq["id"],
            "scheduled_date": "2026-05-01",
        }).json()
        client.patch(f"/api/erp/pm-records/{pm['id']}",
                     json={"status": "in_progress"})
        r = client.patch(f"/api/erp/pm-records/{pm['id']}", json={
            "status": "completed",
            "executed_date": "2026-05-03",
            "performed_by": "TECH-01",
            "result": "ok",
        })
        assert r.status_code == 200
        eq2 = client.get(f"/api/erp/equipments/{eq['id']}").json()
        assert eq2["last_pm_date"] == "2026-05-03"
        assert eq2["next_pm_due"] == "2026-06-02"  # 30 days later

    def test_pm_needs_repair_flips_equipment_to_repair(self, client):
        eq = self._make_equipment(client, "EQ-PM-BRK")
        pm = client.post("/api/erp/pm-records", json={
            "pm_no": "PMR-BRK",
            "equipment_id": eq["id"],
            "scheduled_date": "2026-05-01",
        }).json()
        client.patch(f"/api/erp/pm-records/{pm['id']}",
                     json={"status": "in_progress"})
        client.patch(f"/api/erp/pm-records/{pm['id']}", json={
            "status": "completed",
            "executed_date": "2026-05-03",
            "performed_by": "TECH-02",
            "result": "needs_repair",
            "findings": "主軸軸承異音",
        })
        eq2 = client.get(f"/api/erp/equipments/{eq['id']}").json()
        assert eq2["status"] == "repair"

    def test_cannot_complete_pm_without_executor(self, client):
        eq = self._make_equipment(client, "EQ-PM-NOEX")
        pm = client.post("/api/erp/pm-records", json={
            "pm_no": "PMR-NOEX",
            "equipment_id": eq["id"],
            "scheduled_date": "2026-05-01",
        }).json()
        client.patch(f"/api/erp/pm-records/{pm['id']}",
                     json={"status": "in_progress"})
        r = client.patch(f"/api/erp/pm-records/{pm['id']}", json={
            "status": "completed",
            "executed_date": "2026-05-03",
            "result": "ok",
        })
        assert r.status_code == 422
        assert "performed_by" in r.text

    def test_pm_linked_to_plan(self, client):
        eq = self._make_equipment(client, "EQ-PM-LINK")
        plan = client.post("/api/erp/pm-plans", json={
            "plan_no": "PMP-LINK",
            "equipment_id": eq["id"],
            "interval_days": 30,
        }).json()
        r = client.post("/api/erp/pm-records", json={
            "pm_no": "PMR-LINK",
            "equipment_id": eq["id"],
            "plan_id": plan["id"],
        })
        assert r.status_code == 201
        assert r.json()["plan_id"] == plan["id"]

    def test_pm_linked_to_missing_plan(self, client):
        eq = self._make_equipment(client, "EQ-PM-NOP")
        r = client.post("/api/erp/pm-records", json={
            "pm_no": "PMR-NOP",
            "equipment_id": eq["id"],
            "plan_id": "nonexistent-plan",
        })
        assert r.status_code == 422

    def test_filter_pm_records_by_equipment(self, client):
        eq1 = self._make_equipment(client, "EQ-FLT1")
        eq2 = self._make_equipment(client, "EQ-FLT2")
        for i in range(2):
            client.post("/api/erp/pm-records", json={
                "pm_no": f"PMR-F1-{i}", "equipment_id": eq1["id"],
            })
        client.post("/api/erp/pm-records", json={
            "pm_no": "PMR-F2-0", "equipment_id": eq2["id"],
        })
        r = client.get(f"/api/erp/pm-records?equipment_id={eq1['id']}")
        assert r.status_code == 200
        assert len(r.json()) == 2
