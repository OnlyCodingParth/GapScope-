"""Backend-only, optional Gemini enrichment for verified learning-gap data."""

import json
import logging
from typing import Any

import requests
from pydantic import BaseModel, Field, ValidationError, field_validator

from app.core.config import get_settings

logger = logging.getLogger(__name__)

AI_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["insights", "practice_questions"],
    "properties": {
        "insights": {
            "type": "array",
            "items": {
                "type": "object", "additionalProperties": False,
                "required": ["misconception_id", "explanation", "recommendation"],
                "properties": {"misconception_id": {"type": "string"}, "explanation": {"type": "string"}, "recommendation": {"type": "string"}},
            },
        },
        "practice_questions": {
            "type": "array",
            "items": {
                "type": "object", "additionalProperties": False,
                "required": ["target_misconception_id", "question", "options", "correct_option", "explanation"],
                "properties": {
                    "target_misconception_id": {"type": "string"}, "question": {"type": "string"},
                    "options": {"type": "array", "items": {"type": "string"}}, "correct_option": {"type": "string"}, "explanation": {"type": "string"},
                },
            },
        },
    },
}


class GeneratedPracticeQuestion(BaseModel):
    target_misconception_id: str = Field(min_length=1)
    question: str = Field(min_length=8, max_length=500)
    options: list[str] = Field(min_length=4, max_length=4)
    correct_option: str = Field(min_length=1, max_length=200)
    explanation: str = Field(min_length=8, max_length=700)

    @field_validator("options")
    @classmethod
    def unique_non_empty_options(cls, options: list[str]) -> list[str]:
        cleaned = [option.strip() for option in options]
        if any(not option for option in cleaned) or len(set(cleaned)) != 4:
            raise ValueError("options must contain four distinct non-empty values")
        return cleaned

    def valid_for(self, misconception_id: str) -> bool:
        return self.target_misconception_id == misconception_id and self.correct_option in self.options


class InsightItem(BaseModel):
    misconception_id: str
    explanation: str = Field(min_length=8, max_length=1000)
    recommendation: str = Field(min_length=8, max_length=1000)


class LlmOutput(BaseModel):
    insights: list[InsightItem] = Field(min_length=1, max_length=9)
    practice_questions: list[GeneratedPracticeQuestion] = Field(default_factory=list, max_length=3)


def _fallback(report: dict[str, object]) -> dict[str, object]:
    insights = [
        {
            "misconception_id": gap["misconception_id"],
            "explanation": f"Your selected answers on {gap['evidence_count']} mapped response(s) point to {gap['misconception_name'].lower()}. {gap['description']}",
            "recommendation": gap["recommendation"],
        }
        for gap in report["gaps"]
    ]
    return {"source": "fallback", "available": False, "message": "AI insight is unavailable, so GapScope is showing the verified deterministic guidance.", "insights": insights, "practice_questions": []}


def _prompt(report: dict[str, object], practice_needed: int) -> str:
    verified_gaps = []
    for gap in report["gaps"]:
        verified_gaps.append({
            "misconception_id": gap["misconception_id"],
            "misconception_name": gap["misconception_name"],
            "description": gap["description"],
            "evidence_count": gap["evidence_count"],
            "confidence": gap["confidence"],
            "evidence": [{"question_id": item["question_id"], "question_text": item["question_text"], "concept": item["concept"], "selected_answer": item["selected_answer"]} for item in gap["evidence"]],
            "taxonomy_recommendation": gap["recommendation"],
        })
    return json.dumps({
        "instruction": "You are explaining a verified learning misconception. Do not invent evidence. Do not change the detected misconception. Use only the supplied evidence. Write concise student-friendly explanations and recommendations. Return JSON only. If practice questions are requested, make each a four-option quadratic-equations multiple-choice question tied to the strongest verified misconception, include its exact target_misconception_id, and ensure correct_option exactly equals one option.",
        "subject": "Quadratic Equations",
        "verified_gaps": verified_gaps,
        "practice_questions_requested": practice_needed,
    })


def _request_llm(prompt: str) -> dict[str, Any]:
    settings = get_settings()
    response = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{settings.gemini_model}:generateContent",
        headers={"x-goog-api-key": str(settings.gemini_api_key), "Content-Type": "application/json"},
        json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseJsonSchema": AI_SCHEMA,
            },
        },
        timeout=settings.gemini_timeout_seconds,
    )
    response.raise_for_status()
    content = response.json()["candidates"][0]["content"]["parts"][0]["text"]
    return json.loads(content)


def analyze_verified_report(report: dict[str, object], practice_needed: int = 0) -> dict[str, object]:
    """Returns only validated enrichment; all errors degrade to deterministic data."""
    settings = get_settings()
    if not settings.gemini_api_key:
        return _fallback(report)
    try:
        output = LlmOutput.model_validate(_request_llm(_prompt(report, practice_needed)))
        valid_gap_ids = {gap["misconception_id"] for gap in report["gaps"]}
        insights = [item.model_dump() for item in output.insights if item.misconception_id in valid_gap_ids]
        if not insights:
            raise ValueError("No insight referred to a verified misconception")
        strongest_id = report["gaps"][0]["misconception_id"]
        questions = [item.model_dump() for item in output.practice_questions if item.valid_for(strongest_id)][:practice_needed]
        return {"source": "llm", "available": True, "message": "AI insight is based on the verified evidence below.", "insights": insights, "practice_questions": questions}
    except (requests.RequestException, KeyError, TypeError, ValueError, ValidationError, json.JSONDecodeError) as error:
        logger.warning("AI learning insight unavailable; using deterministic fallback: %s", type(error).__name__)
        return _fallback(report)
