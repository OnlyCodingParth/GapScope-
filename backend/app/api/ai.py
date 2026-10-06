from fastapi import APIRouter, Cookie, Depends

from app.schemas.attempt import AiAnalysisRequest
from app.services.ai import analyze_verified_report
from app.services.attempts import get_learning_gap_report
from app.services.auth import require_user_id

router = APIRouter(prefix="/ai")


def current_student(gapscope_session: str | None = Cookie(default=None)) -> str:
    return require_user_id(gapscope_session)


@router.post("/analyze")
def analyze_attempt(request: AiAnalysisRequest, student_id: str = Depends(current_student)) -> dict[str, object]:
    # The client supplies only an owned attempt reference; all evidence is loaded and verified here.
    report = get_learning_gap_report(request.attempt_id, student_id)
    return analyze_verified_report(report)
