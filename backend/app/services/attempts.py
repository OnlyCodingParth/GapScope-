import json
from datetime import UTC, datetime
from uuid import uuid4

from fastapi import HTTPException

from app.core.database import connect
from app.schemas.attempt import AttemptSubmission, SubmittedResponse


def get_quiz_questions() -> list[dict[str, object]]:
    with connect() as connection:
        questions = []
        for row in connection.execute("SELECT id, question_text, concept, difficulty, question_type, options_json FROM questions WHERE id NOT LIKE 'AI-%' ORDER BY id"):
            question = dict(row)
            question["options"] = json.loads(question.pop("options_json"))
            questions.append(question)
        return questions


def grade_attempt(submission: AttemptSubmission, student_id: str) -> dict[str, object]:
    submitted_by_question = {response.question_id: response.selected_answer for response in submission.responses}
    if len(submitted_by_question) != len(submission.responses):
        raise HTTPException(status_code=422, detail="Each question may be submitted only once.")

    with connect() as connection:
        questions = {row["id"]: row for row in connection.execute("SELECT * FROM questions WHERE id NOT LIKE 'AI-%'")}
        if set(submitted_by_question) != set(questions):
            raise HTTPException(status_code=422, detail="Submit exactly one response for every quiz question.")
        graded_responses = grade_responses(submitted_by_question, set(questions), connection, questions)

        attempt_id = str(uuid4())
        correct_answers = sum(response[2] for response in graded_responses)
        total_questions = len(graded_responses)
        percentage = round(correct_answers / total_questions * 100, 2)
        connection.execute(
            "INSERT INTO quiz_attempts VALUES (?, ?, ?, ?, ?, ?)",
            (attempt_id, student_id, datetime.now(UTC).isoformat(), total_questions, correct_answers, percentage),
        )
        connection.executemany(
            "INSERT INTO student_responses VALUES (?, ?, ?, ?, ?)",
            [(attempt_id, *response) for response in graded_responses],
        )
    return get_attempt_result(attempt_id, student_id)


def grade_responses(
    submitted_by_question: dict[str, str], expected_question_ids: set[str], connection, questions: dict[str, object] | None = None,
) -> list[tuple[str, str, int, str | None]]:
    """Shared deterministic grading for original attempts, practice, and retests."""
    if set(submitted_by_question) != expected_question_ids:
        raise HTTPException(status_code=422, detail="Submit exactly one response for every assigned question.")
    if questions is None:
        questions = {row["id"]: row for row in connection.execute("SELECT * FROM questions WHERE id IN ({})".format(",".join("?" for _ in expected_question_ids)), tuple(expected_question_ids))}
    graded_responses: list[tuple[str, str, int, str | None]] = []
    for question_id, selected_answer in submitted_by_question.items():
        question = questions.get(question_id)
        if question is None:
            raise HTTPException(status_code=422, detail=f"Unknown question ID: {question_id}")
        if selected_answer not in json.loads(question["options_json"]):
            raise HTTPException(status_code=422, detail=f"Invalid answer option for {question_id}.")
        is_correct = selected_answer == question["correct_answer"]
        misconception_id = None
        if not is_correct:
            mapping = connection.execute(
                "SELECT misconception_id FROM misconception_mappings WHERE question_id = ? AND incorrect_option = ?",
                (question_id, selected_answer),
            ).fetchone()
            misconception_id = mapping["misconception_id"] if mapping else None
        graded_responses.append((question_id, selected_answer, int(is_correct), misconception_id))
    return graded_responses


def get_attempt_result(attempt_id: str, student_id: str) -> dict[str, object]:
    with connect() as connection:
        attempt = connection.execute("SELECT * FROM quiz_attempts WHERE id = ? AND student_id = ?", (attempt_id, student_id)).fetchone()
        if attempt is None:
            raise HTTPException(status_code=404, detail="Attempt not found.")
        results = [
            dict(row)
            for row in connection.execute(
                """SELECT r.question_id, r.selected_answer, r.is_correct, r.misconception_id,
                m.name AS misconception_name FROM student_responses r
                LEFT JOIN misconceptions m ON m.id = r.misconception_id
                WHERE r.attempt_id = ? ORDER BY r.question_id""",
                (attempt_id,),
            )
        ]
        detected = []
        seen = set()
        for result in results:
            misconception_id = result["misconception_id"]
            if misconception_id and misconception_id not in seen:
                detected.append({"id": misconception_id, "name": result["misconception_name"]})
                seen.add(misconception_id)
        data = dict(attempt)
        data["incorrect_answers"] = data["total_questions"] - data["correct_answers"]
        data["score"] = data["correct_answers"]
        data["results"] = results
        data["detected_misconceptions"] = detected
        return data


def get_learning_gap_report(attempt_id: str, student_id: str) -> dict[str, object]:
    """Build a small, deterministic report from this student's submitted answers only."""
    # Keep ownership and missing-attempt behavior identical to the attempt endpoint.
    attempt = get_attempt_result(attempt_id, student_id)
    with connect() as connection:
        evidence_rows = connection.execute(
            """SELECT r.question_id, q.question_text, q.concept, r.selected_answer,
                      r.misconception_id, m.name AS misconception_name, m.description AS misconception_description
               FROM student_responses r
               JOIN questions q ON q.id = r.question_id
               JOIN misconceptions m ON m.id = r.misconception_id
               WHERE r.attempt_id = ? AND r.is_correct = 0 AND r.misconception_id IS NOT NULL
               ORDER BY r.question_id""",
            (attempt_id,),
        ).fetchall()

    grouped: dict[str, dict[str, object]] = {}
    for row in evidence_rows:
        item = grouped.setdefault(
            row["misconception_id"],
            {
                "misconception_id": row["misconception_id"],
                "misconception_name": row["misconception_name"],
                "description": row["misconception_description"],
                "evidence": [],
            },
        )
        item["evidence"].append({
            "question_id": row["question_id"],
            "question_text": row["question_text"],
            "concept": row["concept"],
            "selected_answer": row["selected_answer"],
        })

    gaps = []
    for item in grouped.values():
        evidence = item["evidence"]
        evidence_count = len(evidence)
        confidence = "high" if evidence_count >= 3 else "medium" if evidence_count == 2 else "low"
        gaps.append({
            **item,
            "evidence_count": evidence_count,
            "confidence": confidence,
            "recommendation": f"Review {item['misconception_name'].lower()}: {item['description']}",
        })
    gaps.sort(key=lambda gap: (-gap["evidence_count"], str(gap["misconception_name"])))

    return {
        "attempt_id": attempt["id"],
        "total_questions": attempt["total_questions"],
        "correct_answers": attempt["correct_answers"],
        "gaps": gaps,
        "chart": [
            {"misconception_id": gap["misconception_id"], "label": gap["misconception_name"], "evidence_count": gap["evidence_count"]}
            for gap in gaps
        ],
    }
