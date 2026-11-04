"""Shared pytest fixtures for isolated database-layer tests."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import database


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    """Create a fresh SQLite database for every test."""
    monkeypatch.setattr(database, 'DB_PATH', tmp_path / 'test_corkboard.db')
    database.initialize()
    return database


@pytest.fixture
def create_note(test_db):
    """Create a valid note and return its generated ID."""
    def _create_note(title='Test note'):
        with test_db.connect() as conn:
            cursor = conn.execute(
                """INSERT INTO notes (board_id, title, body, x, y)
                   VALUES (1, ?, 'Sample body', 100, 100)""",
                (title,),
            )
            return cursor.lastrowid
    return _create_note
