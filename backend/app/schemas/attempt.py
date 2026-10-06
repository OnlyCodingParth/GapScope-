from pydantic import BaseModel, Field


class SubmittedResponse(BaseModel):
    question_id: str = Field(min_length=1)
    selected_answer: str = Field(min_length=1)


class AttemptSubmission(BaseModel):
    responses: list[SubmittedResponse] = Field(min_length=1)


class PracticeStart(BaseModel):
    source_attempt_id: str = Field(min_length=1)


class AiAnalysisRequest(BaseModel):
    attempt_id: str = Field(min_length=1)


class PracticeSubmission(AttemptSubmission):
    stage: str = Field(pattern="^(practice|retest)$")
