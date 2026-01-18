"""
Shared test fixtures for Jeopardy tests.

Fixtures are reusable test setup. This file is automatically
loaded by pytest - you don't need to import it.

Learn more about fixtures: https://docs.pytest.org/en/stable/fixture.html
"""

import pytest
from pathlib import Path
import tempfile
import json


@pytest.fixture
def sample_clues() -> list[dict]:
    """
    A small set of valid test clues.

    Use this when you need predictable test data.

    Example:
        def test_something(sample_clues):
            assert len(sample_clues) == 5
    """
    return [
        {
            "category": "SCIENCE",
            "value": 200,
            "question": "This planet is known as the Red Planet",
            "answer": "Mars",
            "round": "Jeopardy!",
            "show_number": 1000,
            "air_date": "2020-01-01"
        },
        {
            "category": "SCIENCE",
            "value": 400,
            "question": "The chemical symbol for gold",
            "answer": "Au",
            "round": "Jeopardy!",
            "show_number": 1000,
            "air_date": "2020-01-01"
        },
        {
            "category": "SCIENCE",
            "value": 600,
            "question": "This force keeps planets in orbit",
            "answer": "Gravity",
            "round": "Jeopardy!",
            "show_number": 1000,
            "air_date": "2020-01-01"
        },
        {
            "category": "HISTORY",
            "value": 200,
            "question": "The first President of the United States",
            "answer": "George Washington",
            "round": "Jeopardy!",
            "show_number": 1000,
            "air_date": "2020-01-01"
        },
        {
            "category": "HISTORY",
            "value": 400,
            "question": "This document was signed in 1776",
            "answer": "The Declaration of Independence",
            "round": "Jeopardy!",
            "show_number": 1000,
            "air_date": "2020-01-01"
        },
    ]


@pytest.fixture
def invalid_clues() -> list[dict]:
    """Clues that should fail validation."""
    return [
        # Missing category
        {
            "category": "",
            "value": 400,
            "question": "Test question",
            "answer": "Test answer"
        },
        # Missing answer
        {
            "category": "SCIENCE",
            "value": 400,
            "question": "Test question",
            "answer": ""
        },
        # Video clue reference
        {
            "category": "SCIENCE",
            "value": 400,
            "question": "[video clue] This animal is shown here",
            "answer": "Elephant"
        },
        # Audio clue reference
        {
            "category": "MUSIC",
            "value": 400,
            "question": "[audio clue] Name this composer",
            "answer": "Mozart"
        },
    ]


@pytest.fixture
def temp_db(tmp_path) -> Path:
    """
    Create a temporary database path for testing.

    The database file won't exist yet - tests create it.
    It's automatically cleaned up after the test.
    """
    return tmp_path / "test_jeopardy.db"


@pytest.fixture
def temp_json_file(tmp_path, sample_clues) -> Path:
    """
    Create a temporary JSON file with sample clues.

    Useful for testing file loading functions.
    """
    filepath = tmp_path / "test_clues.json"
    filepath.write_text(json.dumps(sample_clues))
    return filepath


@pytest.fixture
def populated_db(temp_db, sample_clues):
    """
    A database with sample clues already loaded.

    Use this when testing query functions.
    """
    # Import here to avoid circular imports
    from jeopardy.database import create_database, load_clues_to_db

    create_database(temp_db)
    load_clues_to_db(sample_clues, temp_db)
    return temp_db
