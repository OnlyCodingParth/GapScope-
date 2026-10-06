import json
import sqlite3
from pathlib import Path

from app.data.quadratics import MAPPINGS, MISCONCEPTIONS, PREREQUISITES, QUESTIONS

DATABASE_PATH = Path(__file__).resolve().parents[2] / "data" / "gapscope.db"


def connect(database_path: Path = DATABASE_PATH) -> sqlite3.Connection:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database(database_path: Path = DATABASE_PATH) -> None:
    with connect(database_path) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS questions (
                id TEXT PRIMARY KEY, question_text TEXT NOT NULL, concept TEXT NOT NULL,
                difficulty TEXT NOT NULL, question_type TEXT NOT NULL, options_json TEXT NOT NULL,
                correct_answer TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS misconceptions (
                id TEXT PRIMARY KEY, name TEXT NOT NULL, description TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS misconception_mappings (
                question_id TEXT NOT NULL, incorrect_option TEXT NOT NULL, misconception_id TEXT NOT NULL,
                PRIMARY KEY (question_id, incorrect_option),
                FOREIGN KEY (question_id) REFERENCES questions(id),
                FOREIGN KEY (misconception_id) REFERENCES misconceptions(id)
            );
            CREATE TABLE IF NOT EXISTS prerequisites (
                prerequisite_concept TEXT NOT NULL, dependent_concept TEXT NOT NULL,
                PRIMARY KEY (prerequisite_concept, dependent_concept)
            );
            CREATE TABLE IF NOT EXISTS quiz_attempts (
                id TEXT PRIMARY KEY, student_id TEXT NOT NULL, created_at TEXT NOT NULL,
                total_questions INTEGER NOT NULL, correct_answers INTEGER NOT NULL,
                percentage REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS student_responses (
                attempt_id TEXT NOT NULL, question_id TEXT NOT NULL, selected_answer TEXT NOT NULL,
                is_correct INTEGER NOT NULL, misconception_id TEXT,
                PRIMARY KEY (attempt_id, question_id),
                FOREIGN KEY (attempt_id) REFERENCES quiz_attempts(id),
                FOREIGN KEY (question_id) REFERENCES questions(id),
                FOREIGN KEY (misconception_id) REFERENCES misconceptions(id)
            );
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY, google_sub TEXT NOT NULL UNIQUE, email TEXT NOT NULL,
                name TEXT NOT NULL, picture TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY, user_id TEXT NOT NULL, expires_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            CREATE TABLE IF NOT EXISTS practice_sessions (
                id TEXT PRIMARY KEY, student_id TEXT NOT NULL, source_attempt_id TEXT NOT NULL,
                misconception_id TEXT NOT NULL, before_evidence_count INTEGER NOT NULL,
                before_confidence TEXT NOT NULL, created_at TEXT NOT NULL,
                FOREIGN KEY (source_attempt_id) REFERENCES quiz_attempts(id),
                FOREIGN KEY (misconception_id) REFERENCES misconceptions(id)
            );
            CREATE TABLE IF NOT EXISTS practice_responses (
                practice_id TEXT NOT NULL, stage TEXT NOT NULL CHECK(stage IN ('practice', 'retest')),
                question_id TEXT NOT NULL, selected_answer TEXT NOT NULL, is_correct INTEGER NOT NULL,
                PRIMARY KEY (practice_id, stage, question_id),
                FOREIGN KEY (practice_id) REFERENCES practice_sessions(id),
                FOREIGN KEY (question_id) REFERENCES questions(id)
            );
            CREATE TABLE IF NOT EXISTS practice_questions (
                practice_id TEXT NOT NULL, question_id TEXT NOT NULL, position INTEGER NOT NULL,
                PRIMARY KEY (practice_id, question_id),
                FOREIGN KEY (practice_id) REFERENCES practice_sessions(id),
                FOREIGN KEY (question_id) REFERENCES questions(id)
            );
            """
        )
        connection.executemany(
            """INSERT INTO questions VALUES (?, ?, ?, ?, 'multiple_choice', ?, ?)
            ON CONFLICT(id) DO UPDATE SET question_text=excluded.question_text, concept=excluded.concept,
            difficulty=excluded.difficulty, question_type=excluded.question_type,
            options_json=excluded.options_json, correct_answer=excluded.correct_answer""",
            [(identifier, text, concept, difficulty, json.dumps(options), answer) for identifier, text, concept, difficulty, options, answer in QUESTIONS],
        )
        connection.executemany("INSERT INTO misconceptions VALUES (?, ?, ?) ON CONFLICT(id) DO UPDATE SET name=excluded.name, description=excluded.description", MISCONCEPTIONS)
        connection.executemany("INSERT INTO misconception_mappings VALUES (?, ?, ?) ON CONFLICT(question_id, incorrect_option) DO UPDATE SET misconception_id=excluded.misconception_id", MAPPINGS)
        connection.executemany("INSERT INTO prerequisites VALUES (?, ?) ON CONFLICT(prerequisite_concept, dependent_concept) DO NOTHING", PREREQUISITES)
