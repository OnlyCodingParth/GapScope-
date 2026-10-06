from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.main import app
from app.services import ai
from tests.test_attempts import complete_submission, sign_in


def report_with_gap(client: TestClient) -> dict[str, object]:
    responses = complete_submission(client)
    responses[0]["selected_answer"] = "x = −2 or −3"
    attempt = client.post("/api/attempts", json={"responses": responses}).json()
    return client.get(f"/api/attempts/{attempt['id']}/report").json()


def configured(monkeypatch) -> None:
    monkeypatch.setattr(ai, "get_settings", lambda: SimpleNamespace(gemini_api_key="test-key", gemini_model="test-model", gemini_timeout_seconds=1))


def valid_output() -> dict[str, object]:
    return {
        "insights": [{"misconception_id": "M01", "explanation": "A changed sign appears in the selected answer, which fits the verified sign-error evidence.", "recommendation": "Check signs after each algebra step and practise moving terms across the equals sign."}],
        "practice_questions": [{"target_misconception_id": "M01", "question": "Which solution correctly solves x² − x − 2 = 0?", "options": ["x = 2 or −1", "x = −2 or 1", "x = 2 only", "x = −1 only"], "correct_option": "x = 2 or −1", "explanation": "The factors are (x − 2)(x + 1), so the signs give 2 and −1."}],
    }


def test_ai_endpoint_is_authenticated_and_attempt_owned(monkeypatch) -> None:
    with TestClient(app) as anonymous:
        assert anonymous.post("/api/ai/analyze", json={"attempt_id": "missing"}).status_code == 401

    with TestClient(app) as owner:
        sign_in(owner, "ai-owner")
        report = report_with_gap(owner)
        configured(monkeypatch)
        monkeypatch.setattr(ai, "_request_llm", lambda _: valid_output())
        response = owner.post("/api/ai/analyze", json={"attempt_id": report["attempt_id"]})
        assert response.status_code == 200
        assert response.json()["source"] == "llm"
        assert response.json()["insights"][0]["misconception_id"] == "M01"

    with TestClient(app) as other:
        sign_in(other, "ai-other")
        assert other.post("/api/ai/analyze", json={"attempt_id": report["attempt_id"]}).status_code == 404


def test_malformed_or_invalid_ai_output_uses_safe_fallback(monkeypatch) -> None:
    with TestClient(app) as client:
        sign_in(client, "ai-fallback")
        report = report_with_gap(client)
        configured(monkeypatch)
        monkeypatch.setattr(ai, "_request_llm", lambda _: {"not": "the expected schema"})
        fallback = ai.analyze_verified_report(report)
        assert fallback["source"] == "fallback"
        assert fallback["practice_questions"] == []

        bad = valid_output()
        bad["practice_questions"][0]["correct_option"] = "not an option"
        monkeypatch.setattr(ai, "_request_llm", lambda _: bad)
        accepted = ai.analyze_verified_report(report, practice_needed=1)
        assert accepted["source"] == "llm"
        assert accepted["practice_questions"] == []
