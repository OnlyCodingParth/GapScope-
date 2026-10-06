from fastapi import APIRouter, Cookie, Depends

from app.schemas.attempt import AttemptSubmission, PracticeStart, PracticeSubmission
from app.services.auth import require_user_id
from app.services.attempts import get_attempt_result, get_learning_gap_report, get_quiz_questions, grade_attempt
from app.services.practice import get_practice, start_practice, submit_practice

router = APIRouter()


@router.get("/quiz/questions")
def list_quiz_questions() -> list[dict[str, object]]:
    return get_quiz_questions()


def current_student(gapscope_session: str | None = Cookie(default=None)) -> str:
    return require_user_id(gapscope_session)


@router.post("/attempts", status_code=201)
def submit_attempt(submission: AttemptSubmission, student_id: str = Depends(current_student)) -> dict[str, object]:
    return grade_attempt(submission, student_id)


@router.get("/attempts/{attempt_id}")
def retrieve_attempt(attempt_id: str, student_id: str = Depends(current_student)) -> dict[str, object]:
    return get_attempt_result(attempt_id, student_id)


@router.get("/attempts/{attempt_id}/report")
def retrieve_learning_gap_report(attempt_id: str, student_id: str = Depends(current_student)) -> dict[str, object]:
    return get_learning_gap_report(attempt_id, student_id)


@router.post("/practice", status_code=201)
def create_practice(request: PracticeStart, student_id: str = Depends(current_student)) -> dict[str, object]:
    return start_practice(request.source_attempt_id, student_id)


@router.get("/practice/{practice_id}")
def retrieve_practice(practice_id: str, student_id: str = Depends(current_student)) -> dict[str, object]:
    return get_practice(practice_id, student_id)


@router.post("/practice/{practice_id}/submit")
def grade_practice(practice_id: str, submission: PracticeSubmission, student_id: str = Depends(current_student)) -> dict[str, object]:
    return submit_practice(practice_id, submission, student_id)
