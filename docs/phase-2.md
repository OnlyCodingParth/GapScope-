# Phase 2: data foundation

GapScope now has a local SQLite foundation for its Quadratic Equations MVP. The backend initializes and idempotently seeds `backend/data/gapscope.db` on startup.

## Seed data

- 16 multiple-choice questions, from basic to harder
- 9 deterministic misconception definitions
- 48 wrong-option to misconception mappings
- 8 prerequisite relationships

Every incorrect option is mapped deterministically, so a later diagnosis engine can use the data without an AI classifier.

## Commands

From `backend`, run `python -m app.seed` to seed the database manually. It is safe to run again. Start the API with `uvicorn app.main:app --reload --port 8000`; it seeds automatically. Run `python -m pytest` to check the data and APIs.

## APIs

`GET /api/questions`, `GET /api/misconceptions`, `GET /api/misconception-mappings`, and `GET /api/prerequisites` return the seeded data. These APIs are deliberately read-only.

## Boundaries

Phase 2 does not implement quizzes, answer submission, diagnosis, authentication, reports, recommendations, AI, or analytics. The next phase can add grading against the stable question IDs and correct answers.
