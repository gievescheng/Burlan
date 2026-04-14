"""Tests for Management Review (ISO 9001:2015 §9.3)."""
from __future__ import annotations

from erp_qms_core.domain.transitions import validate_status_transition
from erp_qms_core.repositories import review as review_repo


# ── Domain transitions ─────────────────────────────────

class TestReviewTransitions:
    def test_planned_to_in_progress(self):
        assert validate_status_transition(
            "management_review", "planned", "in_progress",
        ) is None

    def test_in_progress_to_closed(self):
        assert validate_status_transition(
            "management_review", "in_progress", "closed",
        ) is None

    def test_skip_in_progress_blocked(self):
        err = validate_status_transition(
            "management_review", "planned", "closed",
        )
        assert err is not None

    def test_closed_is_terminal(self):
        err = validate_status_transition(
            "management_review", "closed", "planned",
        )
        assert err is not None


class TestReviewActionTransitions:
    def test_open_to_in_progress(self):
        assert validate_status_transition(
            "review_action", "open", "in_progress",
        ) is None

    def test_in_progress_to_completed(self):
        assert validate_status_transition(
            "review_action", "in_progress", "completed",
        ) is None

    def test_completed_is_terminal(self):
        err = validate_status_transition(
            "review_action", "completed", "in_progress",
        )
        assert err is not None


# ── Review Repository ──────────────────────────────────

class TestReviewRepository:
    def test_create_review(self, db_session):
        r = review_repo.create_review(db_session, {
            "review_no": "MR-2026-Q1",
            "meeting_type": "regular",
            "chairperson": "CEO",
        })
        db_session.flush()
        assert r.review_no == "MR-2026-Q1"
        assert r.status == "planned"


# ── Review API ─────────────────────────────────────────

class TestReviewAPI:
    def test_create_review(self, client):
        r = client.post("/api/erp/management-reviews", json={
            "review_no": "MR-API-01",
            "meeting_type": "regular",
            "chairperson": "GM",
            "meeting_date": "2026-06-01",
        })
        assert r.status_code == 201
        assert r.json()["review_no"] == "MR-API-01"

    def test_invalid_meeting_type_422(self, client):
        r = client.post("/api/erp/management-reviews", json={
            "review_no": "MR-BAD", "meeting_type": "unscheduled",
        })
        assert r.status_code == 422

    def test_duplicate_review_no_409(self, client):
        client.post("/api/erp/management-reviews", json={"review_no": "MR-DUP"})
        r = client.post("/api/erp/management-reviews", json={"review_no": "MR-DUP"})
        assert r.status_code == 409

    def test_cannot_close_review_without_required_inputs(self, client):
        """ISO §9.3.2 — 結案前必須完成核心輸入"""
        rev = client.post("/api/erp/management-reviews", json={
            "review_no": "MR-EMPTY", "chairperson": "GM",
        }).json()
        client.patch(f"/api/erp/management-reviews/{rev['id']}",
                     json={"status": "in_progress"})
        r = client.patch(f"/api/erp/management-reviews/{rev['id']}",
                         json={"status": "closed"})
        assert r.status_code == 422
        assert "required §9.3.2 inputs" in r.text

    def test_close_review_with_all_inputs(self, client):
        rev = client.post("/api/erp/management-reviews", json={
            "review_no": "MR-FULL",
            "chairperson": "GM",
            "attendees": "All managers",
        }).json()
        # 填齊必要輸入 → in_progress → closed
        client.patch(f"/api/erp/management-reviews/{rev['id']}",
                     json={"status": "in_progress"})
        r = client.patch(f"/api/erp/management-reviews/{rev['id']}", json={
            "status": "closed",
            "qms_performance_summary": "達成率 95%",
            "audit_results_summary": "2 件稽核全部關閉",
            "nc_and_ca_summary": "NCR 5 件、CAPA 3 件均結案",
            "customer_satisfaction_summary": "客戶滿意度 92 分",
            "improvement_decisions": "建立電子化表單系統",
            "closed_by": "CEO",
        })
        assert r.status_code == 200
        assert r.json()["status"] == "closed"

    def test_review_action_lifecycle(self, client):
        """審查 → 行動項目 → 完成"""
        rev = client.post("/api/erp/management-reviews", json={
            "review_no": "MR-ACT", "chairperson": "GM",
        }).json()
        # 建立行動
        r = client.post("/api/erp/review-actions", json={
            "action_no": "RA-01",
            "review_id": rev["id"],
            "action_type": "improvement",
            "description": "建立電子化表單系統",
            "responsible_person": "IT-01",
            "due_date": "2026-09-30",
        })
        assert r.status_code == 201
        action_id = r.json()["id"]

        # open → in_progress
        r2 = client.patch(f"/api/erp/review-actions/{action_id}", json={
            "status": "in_progress",
        })
        assert r2.status_code == 200

        # in_progress → completed
        r3 = client.patch(f"/api/erp/review-actions/{action_id}", json={
            "status": "completed",
            "completion_date": "2026-09-15",
            "effectiveness_check": "系統已上線使用 2 個月穩定",
        })
        assert r3.status_code == 200

    def test_invalid_action_type_422(self, client):
        rev = client.post("/api/erp/management-reviews", json={
            "review_no": "MR-AT", "chairperson": "GM",
        }).json()
        r = client.post("/api/erp/review-actions", json={
            "action_no": "RA-BAD",
            "review_id": rev["id"],
            "action_type": "wishlist",
        })
        assert r.status_code == 422

    def test_action_for_missing_review(self, client):
        r = client.post("/api/erp/review-actions", json={
            "action_no": "RA-ORPH", "review_id": "nonexistent",
        })
        assert r.status_code == 422

    def test_action_linked_to_capa(self, client):
        """審查行動可連結至 CAPA"""
        capa = client.post("/api/erp/capas", json={
            "capa_no": "CAPA-MR", "subject": "from management review",
            "source_type": "management_review",
        }).json()
        rev = client.post("/api/erp/management-reviews", json={
            "review_no": "MR-CAPA", "chairperson": "GM",
        }).json()
        r = client.post("/api/erp/review-actions", json={
            "action_no": "RA-CAPA",
            "review_id": rev["id"],
            "action_type": "qms_change",
            "description": "updating procedures",
            "capa_id": capa["id"],
        })
        assert r.status_code == 201
        assert r.json()["capa_id"] == capa["id"]

    def test_action_linked_to_missing_capa(self, client):
        rev = client.post("/api/erp/management-reviews", json={
            "review_no": "MR-BADCAPA", "chairperson": "GM",
        }).json()
        r = client.post("/api/erp/review-actions", json={
            "action_no": "RA-BADCAPA", "review_id": rev["id"],
            "capa_id": "nonexistent-capa",
        })
        assert r.status_code == 422

    def test_filter_actions_by_review(self, client):
        rev1 = client.post("/api/erp/management-reviews", json={
            "review_no": "MR-F1", "chairperson": "GM",
        }).json()
        rev2 = client.post("/api/erp/management-reviews", json={
            "review_no": "MR-F2", "chairperson": "GM",
        }).json()
        for i in range(3):
            client.post("/api/erp/review-actions", json={
                "action_no": f"RA-F1-{i}", "review_id": rev1["id"],
            })
        client.post("/api/erp/review-actions", json={
            "action_no": "RA-F2-0", "review_id": rev2["id"],
        })
        r = client.get(f"/api/erp/review-actions?review_id={rev1['id']}")
        assert r.status_code == 200
        assert len(r.json()) == 3
