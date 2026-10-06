# Phase 3: student responses and deterministic grading

The student preview now demonstrates a complete Quadratic Equations attempt: load questions, select every answer, submit, and view a server-calculated result.

## APIs

- `GET /api/quiz/questions` returns quiz-safe questions without correct answers.
- `POST /api/attempts` accepts `student_id` and one `question_id` / `selected_answer` pair per question, grades them deterministically, and returns the result.
- `GET /api/attempts/{attempt_id}` retrieves a stored result.

## Database

SQLite now includes `quiz_attempts` and `student_responses`. Phase 3 uses `demo-student` only; no authentication is involved. Each saved incorrect answer uses the exact Phase 2 wrong-option mapping where applicable.

## Verification

Run `python -m pytest` from `backend` and `npm run build` from `frontend`. The tests cover correct and incorrect grading, misconception mapping, score calculation, invalid question/option/duplicate rejection, and result retrieval.

## Boundary

This phase does not diagnose learning gaps, calculate confidence or severity, create reports or recommendations, or provide AI functionality.
