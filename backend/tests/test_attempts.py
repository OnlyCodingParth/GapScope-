from fastapi.testclient import TestClient

from app.main import app


def sign_in(client: TestClient, sub: str = "google-user-1") -> dict[str, str]:
    from app.api import auth

    original = auth.verify_google_credential
    auth.verify_google_credential = lambda _: {"sub": sub, "email": f"{sub}@example.test", "name": "Demo Student"}
    try:
        response = client.post("/api/auth/google", json={"credential": "test-credential"})
    finally:
        auth.verify_google_credential = original
    assert response.status_code == 200
    return response.json()["user"]


def complete_submission(client: TestClient) -> list[dict[str, str]]:
    questions = client.get("/api/quiz/questions").json()
    content_questions = {question["id"]: question for question in client.get("/api/questions").json()}
    return [
        {"question_id": question["id"], "selected_answer": content_questions[question["id"]]["correct_answer"]}
        for question in questions
    ]


def test_attempt_grades_answers_maps_misconception_and_returns_result() -> None:
    with TestClient(app) as client:
        sign_in(client)
        responses = complete_submission(client)
        responses[0]["selected_answer"] = "x = −2 or −3"
        submitted = client.post("/api/attempts", json={"responses": responses})

        assert submitted.status_code == 201
        result = submitted.json()
        assert result["total_questions"] == 16
        assert result["correct_answers"] == 15
        assert result["incorrect_answers"] == 1
        assert result["score"] == 15
        assert result["percentage"] == 93.75
        first_result = result["results"][0]
        assert first_result == {
            "question_id": "Q01", "selected_answer": "x = −2 or −3", "is_correct": 0,
            "misconception_id": "M01", "misconception_name": "Sign error",
        }
        assert result["detected_misconceptions"] == [{"id": "M01", "name": "Sign error"}]

        fetched = client.get(f"/api/attempts/{result['id']}")
        assert fetched.status_code == 200
        assert fetched.json() == result


def test_attempt_validation_rejects_invalid_question_and_missing_attempt() -> None:
    with TestClient(app) as client:
        sign_in(client)
        responses = complete_submission(client)
        responses[0]["question_id"] = "NOT-A-QUESTION"
        assert client.post("/api/attempts", json={"responses": responses}).status_code == 422
        responses = complete_submission(client)
        responses[0]["selected_answer"] = "not an option"
        assert client.post("/api/attempts", json={"responses": responses}).status_code == 422
        responses = complete_submission(client)
        responses.append(responses[0])
        assert client.post("/api/attempts", json={"responses": responses}).status_code == 422
        assert client.get("/api/attempts/not-a-real-attempt").status_code == 404


def test_learning_gap_report_uses_real_response_evidence_and_counts() -> None:
    with TestClient(app) as client:
        sign_in(client)
        responses = complete_submission(client)
        responses[0]["selected_answer"] = "x = −2 or −3"  # M01
        responses[1]["selected_answer"] = "(x − 3)(x − 4)"  # M01
        responses[7]["selected_answer"] = "x = [2 ± √(2² − 4·3·(−1))]/6"  # M03
        attempt = client.post("/api/attempts", json={"responses": responses}).json()

        report = client.get(f"/api/attempts/{attempt['id']}/report")
        assert report.status_code == 200
        body = report.json()
        assert body["chart"] == [
            {"misconception_id": "M01", "label": "Sign error", "evidence_count": 2},
            {"misconception_id": "M03", "label": "Quadratic formula misuse", "evidence_count": 1},
        ]
        assert body["gaps"][0]["confidence"] == "medium"
        assert body["gaps"][0]["evidence"][0]["question_id"] == "Q01"
        assert "Review sign error" in body["gaps"][0]["recommendation"]


def test_targeted_practice_and_retest_are_owned_and_use_actual_focus() -> None:
    with TestClient(app) as client:
        sign_in(client, "practice-owner")
        responses = complete_submission(client)
        responses[0]["selected_answer"] = "x = −2 or −3"  # M01 is the only detected gap.
        source_attempt = client.post("/api/attempts", json={"responses": responses}).json()
        created = client.post("/api/practice", json={"source_attempt_id": source_attempt["id"]})
        assert created.status_code == 201
        practice = created.json()
        assert practice["focus"]["misconception_id"] == "M01"
        assert practice["before"] == {"evidence_count": 1, "confidence": "low"}
        assert practice["practice"]["total_questions"] > 0
        assert all("correct_answer" not in question for question in practice["practice"]["questions"])

        practice_answers = [
            {"question_id": question["id"], "selected_answer": question["options"][0]}
            for question in practice["practice"]["questions"]
        ]
        completed = client.post(f"/api/practice/{practice['id']}/submit", json={"stage": "practice", "responses": practice_answers})
        assert completed.status_code == 200
        assert completed.json()["practice"]["complete"] is True
        assert completed.json()["retest"]["questions"]

        retest_answers = [
            {"question_id": question["id"], "selected_answer": question["options"][0]}
            for question in completed.json()["retest"]["questions"]
        ]
        retested = client.post(f"/api/practice/{practice['id']}/submit", json={"stage": "retest", "responses": retest_answers})
        assert retested.status_code == 200
        comparison = retested.json()["comparison"]
        assert comparison["retest_total_questions"] == len(retest_answers)
        assert comparison["message"] in {"Improvement detected in this retest.", "Insufficient evidence to confirm improvement."}
        assert client.post(f"/api/practice/{practice['id']}/submit", json={"stage": "retest", "responses": retest_answers}).status_code == 422

    with TestClient(app) as other_student:
        sign_in(other_student, "different-student")
        assert other_student.get(f"/api/practice/{practice['id']}").status_code == 404
