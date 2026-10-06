import json

from app.core.database import connect


def get_questions() -> list[dict[str, object]]:
    with connect() as connection:
        questions = []
        for row in connection.execute("SELECT * FROM questions WHERE id NOT LIKE 'AI-%' ORDER BY id"):
            question = dict(row)
            question["options"] = json.loads(question.pop("options_json"))
            questions.append(question)
        return questions


def get_misconceptions() -> list[dict[str, str]]:
    with connect() as connection:
        return [dict(row) for row in connection.execute("SELECT * FROM misconceptions ORDER BY id")]


def get_mappings() -> list[dict[str, str]]:
    with connect() as connection:
        return [dict(row) for row in connection.execute("SELECT * FROM misconception_mappings ORDER BY question_id, incorrect_option")]


def get_prerequisites() -> list[dict[str, str]]:
    with connect() as connection:
        return [dict(row) for row in connection.execute("SELECT * FROM prerequisites ORDER BY prerequisite_concept, dependent_concept")]
