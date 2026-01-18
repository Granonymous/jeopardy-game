"""
Tests for jeopardy.database module.

These tests use temporary databases to avoid affecting real data.
The temp_db and populated_db fixtures handle setup/cleanup.

Run with: uv run pytest tests/jeopardy/test_database.py -v
"""

import pytest
import sqlite3
from pathlib import Path

from jeopardy import database


class TestCreateDatabase:
    """Tests for database creation."""

    def test_creates_file(self, temp_db):
        """Should create the database file."""
        assert not temp_db.exists()

        database.create_database(temp_db)

        assert temp_db.exists()

    def test_creates_clues_table(self, temp_db):
        """Should create the clues table with correct columns."""
        database.create_database(temp_db)

        # Connect and check table exists
        conn = sqlite3.connect(temp_db)
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='clues'"
        )
        result = cursor.fetchone()
        conn.close()

        assert result is not None

    def test_idempotent(self, temp_db):
        """Calling create_database twice should not error."""
        database.create_database(temp_db)
        database.create_database(temp_db)  # Should not raise


class TestLoadCluesToDb:
    """Tests for loading clues into database."""

    def test_returns_count(self, temp_db, sample_clues):
        """Should return number of clues inserted."""
        database.create_database(temp_db)

        count = database.load_clues_to_db(sample_clues, temp_db)

        assert count == len(sample_clues)

    def test_clues_are_queryable(self, temp_db, sample_clues):
        """Inserted clues should be queryable."""
        database.create_database(temp_db)
        database.load_clues_to_db(sample_clues, temp_db)

        # Query the database directly
        conn = sqlite3.connect(temp_db)
        cursor = conn.execute("SELECT COUNT(*) FROM clues")
        count = cursor.fetchone()[0]
        conn.close()

        assert count == len(sample_clues)

    def test_clear_existing_removes_old_data(self, temp_db, sample_clues):
        """clear_existing=True should remove old data before insert."""
        database.create_database(temp_db)

        # Load twice with clear_existing=True
        database.load_clues_to_db(sample_clues, temp_db, clear_existing=True)
        database.load_clues_to_db(sample_clues, temp_db, clear_existing=True)

        # Should only have one set of clues
        conn = sqlite3.connect(temp_db)
        cursor = conn.execute("SELECT COUNT(*) FROM clues")
        count = cursor.fetchone()[0]
        conn.close()

        assert count == len(sample_clues)


class TestGetRandomClue:
    """Tests for random clue retrieval."""

    def test_returns_matching_category(self, populated_db, sample_clues):
        """Should return clue from correct category."""
        clue = database.get_random_clue("SCIENCE", 200, populated_db)

        assert clue is not None
        assert clue["category"] == "SCIENCE"

    def test_returns_matching_value(self, populated_db, sample_clues):
        """Should return clue with correct value."""
        clue = database.get_random_clue("SCIENCE", 200, populated_db)

        assert clue is not None
        assert clue["value"] == 200

    def test_returns_none_for_missing(self, populated_db):
        """Should return None if no matching clue exists."""
        clue = database.get_random_clue("NONEXISTENT", 200, populated_db)

        assert clue is None

    def test_returns_dict_with_fields(self, populated_db):
        """Returned clue should have expected fields."""
        clue = database.get_random_clue("SCIENCE", 200, populated_db)

        assert clue is not None
        assert "category" in clue
        assert "value" in clue
        assert "question" in clue
        assert "answer" in clue


class TestCountCluesByCategory:
    """Tests for counting clues by category."""

    def test_returns_dict(self, populated_db):
        """Should return a dictionary."""
        counts = database.count_clues_by_category(populated_db)

        assert isinstance(counts, dict)

    def test_counts_correct(self, populated_db, sample_clues):
        """Counts should match actual data."""
        counts = database.count_clues_by_category(populated_db)

        # Count manually from sample_clues
        expected = {}
        for clue in sample_clues:
            cat = clue["category"]
            expected[cat] = expected.get(cat, 0) + 1

        for cat, count in expected.items():
            assert counts.get(cat) == count


class TestGetCategoryValueCounts:
    """Tests for getting value counts within a category."""

    def test_returns_dict(self, populated_db):
        """Should return a dictionary mapping value to count."""
        counts = database.get_category_value_counts("SCIENCE", populated_db)

        assert isinstance(counts, dict)

    def test_values_are_integers(self, populated_db):
        """Keys should be integer values, values should be counts."""
        counts = database.get_category_value_counts("SCIENCE", populated_db)

        for value, count in counts.items():
            assert isinstance(value, int)
            assert isinstance(count, int)
            assert count > 0


class TestGetTotalClueCount:
    """Tests for total clue count."""

    def test_returns_correct_count(self, populated_db, sample_clues):
        """Should return total number of clues."""
        count = database.get_total_clue_count(populated_db)

        assert count == len(sample_clues)

    def test_empty_db_returns_zero(self, temp_db):
        """Empty database should return 0."""
        database.create_database(temp_db)

        count = database.get_total_clue_count(temp_db)

        assert count == 0
