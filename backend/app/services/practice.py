import json
from datetime import UTC, datetime
from uuid import uuid4

from fastapi import HTTPException

from app.core.database import connect
from app.schemas.attempt import PracticeSubmission
from app.services.attempts import get_learning_gap_report, grade_responses
from app.services.ai import analyze_verified_report


def start_practice(source_attempt_id: str, student_id: str) -> dict[str, object]:
    report = get_learning_gap_report(source_attempt_id, student_id)
    if not report["gaps"]:
        raise HTTPException(status_code=422, detail="This attempt has no mapped misconception to practise.")
    strongest_gap = report["gaps"][0]
    practice_id = str(uuid4())
    with connect() as connection:
        question_ids = _question_ids(connection, strongest_gap["misconception_id"])
        if len(question_ids) < 3:
            enrichment = analyze_verified_report(report, 3 - len(question_ids))
            for generated in enrichment["practice_questions"]:
                question_id = f"AI-{uuid4()}"
                connection.execute(
                    "INSERT INTO questions VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (question_id, generated["question"], "ai targeted practice", "intermediate", "multiple_choice", json.dumps(generated["options"]), generated["correct_option"]),
                )
                connection.executemany(
                    "INSERT INTO misconception_mappings VALUES (?, ?, ?)",
                    [(question_id, option, strongest_gap["misconception_id"]) for option in generated["options"] if option != generated["correct_option"]],
                )
                question_ids.append(question_id)
        connection.execute(
            """INSERT INTO practice_sessions VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (practice_id, student_id, source_attempt_id, strongest_gap["misconception_id"], strongest_gap["evidence_count"], strongest_gap["confidence"], datetime.now(UTC).isoformat()),
        )
        connection.executemany("INSERT INTO practice_questions VALUES (?, ?, ?)", [(practice_id, question_id, position) for position, question_id in enumerate(question_ids)])
    return get_practice(practice_id, student_id)


def _question_ids(connection, misconception_id: str) -> list[str]:
    return [row["question_id"] for row in connection.execute(
        """SELECT DISTINCT question_id FROM misconception_mappings
           WHERE misconception_id = ? ORDER BY question_id""", (misconception_id,)
    )][:3]


def _question_data(connection, question_ids: list[str]) -> list[dict[str, object]]:
    if not question_ids:
        return []
    questions = {row["id"]: row for row in connection.execute(
        "SELECT id, question_text, concept, difficulty, question_type, options_json FROM questions WHERE id IN ({})".format(",".join("?" for _ in question_ids)), question_ids
    )}
    return [{**dict(questions[question_id]), "options": json.loads(questions[question_id]["options_json"])} for question_id in question_ids]


def _stage_result(connection, practice_id: str, stage: str, question_ids: list[str], include_questions: bool) -> dict[str, object]:
    responses = list(connection.execute(
        "SELECT question_id, selected_answer, is_correct FROM practice_responses WHERE practice_id = ? AND stage = ? ORDER BY question_id", (practice_id, stage)
    ))
    complete = len(responses) == len(question_ids) and len(question_ids) > 0
    data: dict[str, object] = {"total_questions": len(question_ids), "complete": complete}
    if include_questions:
        data["questions"] = _question_data(connection, question_ids)
    if complete:
        data["correct_answers"] = sum(row["is_correct"] for row in responses)
    return data


def get_practice(practice_id: str, student_id: str) -> dict[str, object]:
    with connect() as connection:
        session = connection.execute(
            """SELECT p.*, m.name AS misconception_name, m.description AS misconception_description
               FROM practice_sessions p JOIN misconceptions m ON m.id = p.misconception_id
               WHERE p.id = ? AND p.student_id = ?""", (practice_id, student_id)
        ).fetchone()
        if session is None:
            raise HTTPException(status_code=404, detail="Practice session not found.")
        question_ids = [row["question_id"] for row in connection.execute("SELECT question_id FROM practice_questions WHERE practice_id = ? ORDER BY position", (practice_id,))]
        if not question_ids:  # Compatible with any Phase 6 session created before this table existed.
            question_ids = _question_ids(connection, session["misconception_id"])
        practice = _stage_result(connection, practice_id, "practice", question_ids, True)
        retest = _stage_result(connection, practice_id, "retest", question_ids, bool(practice["complete"]))
        comparison = None
        if retest["complete"]:
            correct = retest["correct_answers"]
            total = retest["total_questions"]
            confirmed = total >= 2 and correct / total >= 2 / 3
            comparison = {
                "before_evidence_count": session["before_evidence_count"],
                "before_confidence": session["before_confidence"],
                "retest_correct_answers": correct,
                "retest_total_questions": total,
                "status": "improvement_detected" if confirmed else "insufficient_evidence",
                "message": "Improvement detected in this retest." if confirmed else "Insufficient evidence to confirm improvement.",
            }
        return {
            "id": session["id"],
            "source_attempt_id": session["source_attempt_id"],
            "focus": {"misconception_id": session["misconception_id"], "name": session["misconception_name"], "description": session["misconception_description"]},
            "before": {"evidence_count": session["before_evidence_count"], "confidence": session["before_confidence"]},
            "practice": practice,
            "retest": retest,
            "comparison": comparison,
        }


def submit_practice(practice_id: str, submission: PracticeSubmission, student_id: str) -> dict[str, object]:
    submitted = {response.question_id: response.selected_answer for response in submission.responses}
    if len(submitted) != len(submission.responses):
        raise HTTPException(status_code=422, detail="Each practice question may be submitted only once.")
    with connect() as connection:
        session = connection.execute("SELECT * FROM practice_sessions WHERE id = ? AND student_id = ?", (practice_id, student_id)).fetchone()
        if session is None:
            raise HTTPException(status_code=404, detail="Practice session not found.")
        question_ids = [row["question_id"] for row in connection.execute("SELECT question_id FROM practice_questions WHERE practice_id = ? ORDER BY position", (practice_id,))]
        if not question_ids:
            question_ids = _question_ids(connection, session["misconception_id"])
        existing = connection.execute("SELECT 1 FROM practice_responses WHERE practice_id = ? AND stage = ? LIMIT 1", (practice_id, submission.stage)).fetchone()
        if existing:
            raise HTTPException(status_code=422, detail="This stage has already been submitted.")
        if submission.stage == "retest":
            practice_count = connection.execute("SELECT COUNT(*) AS count FROM practice_responses WHERE practice_id = ? AND stage = 'practice'", (practice_id,)).fetchone()["count"]
            if practice_count != len(question_ids):
                raise HTTPException(status_code=422, detail="Complete targeted practice before starting the retest.")
        graded = grade_responses(submitted, set(question_ids), connection)
        connection.executemany(
            "INSERT INTO practice_responses VALUES (?, ?, ?, ?, ?)",
            [(practice_id, submission.stage, question_id, selected_answer, is_correct) for question_id, selected_answer, is_correct, _ in graded],
        )
    return get_practice(practice_id, student_id)
