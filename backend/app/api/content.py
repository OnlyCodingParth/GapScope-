from fastapi import APIRouter

from app.services.content import get_mappings, get_misconceptions, get_prerequisites, get_questions

router = APIRouter()


@router.get("/questions")
def list_questions() -> list[dict[str, object]]:
    return get_questions()


@router.get("/misconceptions")
def list_misconceptions() -> list[dict[str, str]]:
    return get_misconceptions()


@router.get("/misconception-mappings")
def list_misconception_mappings() -> list[dict[str, str]]:
    return get_mappings()


@router.get("/prerequisites")
def list_prerequisites() -> list[dict[str, str]]:
    return get_prerequisites()
