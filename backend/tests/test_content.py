import json

from fastapi.testclient import TestClient

from app.core.database import connect, initialize_database
from app.main import app


def test_seed_is_idempotent_and_relationships_are_valid(tmp_path) -> None:
    database_path = tmp_path / "gapscope.db"
    initialize_database(database_path)
    initialize_database(database_path)

    with connect(database_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM questions").fetchone()[0] == 16
        assert connection.execute("SELECT COUNT(*) FROM misconceptions").fetchone()[0] == 9
        assert connection.execute("SELECT COUNT(*) FROM misconception_mappings").fetchone()[0] == 48
        assert connection.execute("SELECT COUNT(*) FROM prerequisites").fetchone()[0] == 8
        invalid = connection.execute(
            """SELECT COUNT(*) FROM misconception_mappings m
            LEFT JOIN questions q ON q.id = m.question_id
            LEFT JOIN misconceptions x ON x.id = m.misconception_id
            WHERE q.id IS NULL OR x.id IS NULL"""
        ).fetchone()[0]
        assert invalid == 0
        for question in connection.execute("SELECT id, options_json, correct_answer FROM questions"):
            incorrect_options = set(json.loads(question["options_json"])) - {question["correct_answer"]}
            mapped_options = {
                row[0]
                for row in connection.execute(
                    "SELECT incorrect_option FROM misconception_mappings WHERE question_id = ?",
                    (question["id"],),
                )
            }
            assert mapped_options == incorrect_options


def test_content_endpoints_return_seeded_data() -> None:
    with TestClient(app) as client:
        questions = client.get("/api/questions")
        misconceptions = client.get("/api/misconceptions")
        mappings = client.get("/api/misconception-mappings")
        prerequisites = client.get("/api/prerequisites")

    assert questions.status_code == 200
    assert len(questions.json()) == 16
    assert questions.json()[0]["correct_answer"] in questions.json()[0]["options"]
    assert misconceptions.status_code == 200 and len(misconceptions.json()) == 9
    assert mappings.status_code == 200 and len(mappings.json()) == 48
    assert prerequisites.status_code == 200 and len(prerequisites.json()) == 8
