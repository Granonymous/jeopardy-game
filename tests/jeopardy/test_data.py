"""
Tests for jeopardy.data module.

These tests show WHAT to test. Some are implemented as examples,
others are stubs for you to complete.

Run with: uv run pytest tests/jeopardy/test_data.py -v
"""

import pytest
from pathlib import Path

# Import the module we're testing
from jeopardy import data


class TestLoadSampleData:
    """Tests for loading the sample Jeopardy data."""

    def test_returns_list(self):
        """load_sample_data should return a list."""
        result = data.load_sample_data()
        assert isinstance(result, list)

    def test_clues_have_required_fields(self):
        """Each clue should have category, value, question, answer."""
        clues = data.load_sample_data()
        required_fields = ['category', 'value', 'question', 'answer']

        for clue in clues:
            for field in required_fields:
                assert field in clue, f"Clue missing field: {field}"

    def test_sample_has_clues(self):
        """Sample file should have clues (exact count may vary)."""
        clues = data.load_sample_data()
        assert len(clues) > 0, "Sample data should not be empty"


class TestValidateClue:
    """Tests for clue validation."""

    def test_valid_clue_passes(self, sample_clues):
        """A properly formatted clue should be valid."""
        # sample_clues fixture provides valid clues
        for clue in sample_clues:
            assert data.validate_clue(clue) is True

    def test_missing_category_fails(self):
        """Clue without category should be invalid."""
        clue = {
            "category": "",  # Empty!
            "value": 400,
            "question": "Test question",
            "answer": "Test answer"
        }
        assert data.validate_clue(clue) is False

    def test_missing_answer_fails(self):
        """Clue without answer should be invalid."""
        clue = {
            "category": "SCIENCE",
            "value": 400,
            "question": "Test question",
            "answer": ""  # Empty!
        }
        assert data.validate_clue(clue) is False

    def test_video_clue_fails(self):
        """Clue with [video clue] reference should be invalid."""
        clue = {
            "category": "SCIENCE",
            "value": 400,
            "question": "[video clue] This animal is shown",
            "answer": "Elephant"
        }
        assert data.validate_clue(clue) is False

    def test_missing_value_fails(self):
        """Clue without a value should be invalid."""
        clue = {
            "category": "SCIENCE",
            "value": None,
            "question": "Test question",
            "answer": "Test answer"
        }
        assert data.validate_clue(clue) is False


class TestCleanClues:
    """Tests for cleaning/filtering clues."""

    def test_removes_invalid_clues(self, sample_clues, invalid_clues):
        """clean_clues should filter out invalid clues."""
        mixed = sample_clues + invalid_clues
        cleaned = data.clean_clues(mixed)

        # Should have fewer clues after cleaning
        assert len(cleaned) < len(mixed)
        # Should keep all the valid ones
        assert len(cleaned) >= len(sample_clues)

    def test_keeps_valid_clues(self, sample_clues):
        """clean_clues should keep all valid clues."""
        cleaned = data.clean_clues(sample_clues)
        assert len(cleaned) == len(sample_clues)

    def test_returns_list(self, sample_clues):
        """clean_clues should return a list."""
        cleaned = data.clean_clues(sample_clues)
        assert isinstance(cleaned, list)


class TestGetCategories:
    """Tests for extracting unique categories."""

    def test_returns_unique_categories(self, sample_clues):
        """Should return each category only once."""
        categories = data.get_categories(sample_clues)

        # sample_clues has SCIENCE and HISTORY
        assert "SCIENCE" in categories
        assert "HISTORY" in categories

        # No duplicates
        assert len(categories) == len(set(categories))

    def test_returns_sorted_list(self, sample_clues):
        """Categories should be alphabetically sorted."""
        categories = data.get_categories(sample_clues)

        assert categories == sorted(categories)

    def test_empty_list_returns_empty(self):
        """Empty input should return empty list."""
        categories = data.get_categories([])
        assert categories == []


class TestFilterByCategory:
    """Tests for filtering clues by category."""

    def test_returns_matching_clues(self, sample_clues):
        """Should return only clues from the specified category."""
        science_clues = data.filter_by_category(sample_clues, "SCIENCE")

        for clue in science_clues:
            assert clue["category"] == "SCIENCE"

    def test_nonexistent_category_returns_empty(self, sample_clues):
        """Should return empty list for category with no clues."""
        result = data.filter_by_category(sample_clues, "NONEXISTENT")
        assert result == []

    def test_preserves_clue_data(self, sample_clues):
        """Filtered clues should have all original fields."""
        science_clues = data.filter_by_category(sample_clues, "SCIENCE")

        if science_clues:
            clue = science_clues[0]
            assert "question" in clue
            assert "answer" in clue
            assert "value" in clue
