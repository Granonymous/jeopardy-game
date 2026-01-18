"""
Tests for jeopardy.game module.

Focus on testing the pure game logic functions.
These are the most important tests because game logic
must be correct for the game to work!

Run with: uv run pytest tests/jeopardy/test_game.py -v
"""

import pytest
from jeopardy import game


class TestNormalizeAnswer:
    """Tests for answer normalization."""

    def test_lowercase(self):
        """Should convert to lowercase."""
        assert game.normalize_answer("MARS") == "mars"
        assert game.normalize_answer("Mars") == "mars"

    def test_strips_whitespace(self):
        """Should strip leading/trailing whitespace."""
        assert game.normalize_answer("  mars  ") == "mars"

    def test_strips_what_is(self):
        """Should remove 'what is' prefix."""
        result = game.normalize_answer("What is Mars")
        assert result == "mars"

    def test_strips_who_is(self):
        """Should remove 'who is' prefix."""
        result = game.normalize_answer("Who is Einstein")
        assert result == "einstein"

    def test_strips_what_are(self):
        """Should remove 'what are' prefix."""
        result = game.normalize_answer("What are electrons")
        assert result == "electrons"

    def test_strips_punctuation(self):
        """Should remove common punctuation."""
        assert "?" not in game.normalize_answer("Mars?")
        assert "." not in game.normalize_answer("Mars.")

    def test_handles_the_prefix(self):
        """Should handle 'the' at the beginning."""
        # Could either keep or strip "the" - just be consistent
        result = game.normalize_answer("The Beatles")
        # Result should be either "beatles" or "the beatles"
        assert "beatles" in result

    def test_combined_normalization(self):
        """Should handle multiple normalizations together."""
        result = game.normalize_answer("  What is The Beatles?  ")
        assert "beatles" in result
        assert "?" not in result


class TestCheckAnswer:
    """Tests for answer checking."""

    def test_exact_match(self):
        """Exact answers should match."""
        assert game.check_answer("Mars", "Mars") is True

    def test_case_insensitive(self):
        """Matching should be case-insensitive."""
        assert game.check_answer("mars", "Mars") is True
        assert game.check_answer("MARS", "mars") is True

    def test_with_what_is_prefix(self):
        """'What is X' should match 'X'."""
        assert game.check_answer("What is Mars", "Mars") is True
        assert game.check_answer("what is mars", "Mars") is True

    def test_with_who_is_prefix(self):
        """'Who is X' should match 'X'."""
        assert game.check_answer("Who is Einstein", "Einstein") is True

    def test_wrong_answer(self):
        """Wrong answers should not match."""
        assert game.check_answer("Jupiter", "Mars") is False
        assert game.check_answer("What is Jupiter", "Mars") is False

    def test_empty_answer(self):
        """Empty player answer should not match."""
        assert game.check_answer("", "Mars") is False

    def test_whitespace_handling(self):
        """Should handle extra whitespace."""
        assert game.check_answer("  Mars  ", "Mars") is True


class TestCalculateScoreChange:
    """Tests for score calculation."""

    def test_correct_adds_value(self):
        """Correct answer should add the clue value."""
        assert game.calculate_score_change(400, correct=True) == 400
        assert game.calculate_score_change(1000, correct=True) == 1000

    def test_incorrect_subtracts_value(self):
        """Incorrect answer should subtract the clue value."""
        assert game.calculate_score_change(400, correct=False) == -400
        assert game.calculate_score_change(1000, correct=False) == -1000

    def test_zero_value(self):
        """Should handle zero value (edge case)."""
        assert game.calculate_score_change(0, correct=True) == 0
        assert game.calculate_score_change(0, correct=False) == 0


class TestGenerateBoard:
    """Tests for board generation."""

    def test_has_six_categories(self):
        """Board should have exactly 6 categories."""
        categories = ["A", "B", "C", "D", "E", "F"]

        def mock_get_clue(cat, val):
            return {"category": cat, "value": val, "question": "Q", "answer": "A"}

        board = game.generate_board(categories, mock_get_clue)
        assert len(board) == 6

    def test_each_category_has_five_values(self):
        """Each category should have 5 value levels."""
        categories = ["A", "B", "C", "D", "E", "F"]

        def mock_get_clue(cat, val):
            return {"category": cat, "value": val, "question": "Q", "answer": "A"}

        board = game.generate_board(categories, mock_get_clue)

        for category in categories:
            assert len(board[category]) == 5
            for value in game.STANDARD_VALUES:
                assert value in board[category]

    def test_rejects_wrong_category_count(self):
        """Should raise ValueError if not given 6 categories."""
        def mock_get_clue(cat, val):
            return {"category": cat, "value": val, "question": "Q", "answer": "A"}

        with pytest.raises(ValueError):
            game.generate_board(["A", "B", "C"], mock_get_clue)  # Only 3

        with pytest.raises(ValueError):
            game.generate_board(["A", "B", "C", "D", "E", "F", "G"], mock_get_clue)  # 7

    def test_slots_start_unanswered(self):
        """All slots should start as unanswered."""
        categories = ["A", "B", "C", "D", "E", "F"]

        def mock_get_clue(cat, val):
            return {"category": cat, "value": val, "question": "Q", "answer": "A"}

        board = game.generate_board(categories, mock_get_clue)

        for category in board:
            for value in board[category]:
                assert board[category][value]["answered"] is False


class TestIsBoardComplete:
    """Tests for checking if board is complete."""

    def test_new_board_not_complete(self):
        """Fresh board should not be complete."""
        categories = ["A", "B", "C", "D", "E", "F"]

        def mock_get_clue(cat, val):
            return {"category": cat, "value": val, "question": "Q", "answer": "A"}

        board = game.generate_board(categories, mock_get_clue)
        assert game.is_board_complete(board) is False

    def test_fully_answered_board_complete(self):
        """Board with all slots answered should be complete."""
        categories = ["A", "B", "C", "D", "E", "F"]

        def mock_get_clue(cat, val):
            return {"category": cat, "value": val, "question": "Q", "answer": "A"}

        board = game.generate_board(categories, mock_get_clue)

        # Mark all as answered
        for category in board:
            for value in board[category]:
                board[category][value]["answered"] = True

        assert game.is_board_complete(board) is True


class TestGetRemainingClues:
    """Tests for getting remaining clues."""

    def test_new_board_has_30_remaining(self):
        """Fresh board should have 30 remaining (6 categories * 5 values)."""
        categories = ["A", "B", "C", "D", "E", "F"]

        def mock_get_clue(cat, val):
            return {"category": cat, "value": val, "question": "Q", "answer": "A"}

        board = game.generate_board(categories, mock_get_clue)
        remaining = game.get_remaining_clues(board)

        assert len(remaining) == 30

    def test_returns_tuples(self):
        """Should return list of (category, value) tuples."""
        categories = ["A", "B", "C", "D", "E", "F"]

        def mock_get_clue(cat, val):
            return {"category": cat, "value": val, "question": "Q", "answer": "A"}

        board = game.generate_board(categories, mock_get_clue)
        remaining = game.get_remaining_clues(board)

        for item in remaining:
            assert isinstance(item, tuple)
            assert len(item) == 2


class TestMarkClueAnswered:
    """Tests for marking clues as answered."""

    def test_marks_clue_answered(self):
        """Should mark the specified clue as answered."""
        categories = ["A", "B", "C", "D", "E", "F"]

        def mock_get_clue(cat, val):
            return {"category": cat, "value": val, "question": "Q", "answer": "A"}

        board = game.generate_board(categories, mock_get_clue)

        assert board["A"][200]["answered"] is False
        game.mark_clue_answered(board, "A", 200)
        assert board["A"][200]["answered"] is True

    def test_returns_false_for_invalid(self):
        """Should return False for non-existent clue."""
        categories = ["A", "B", "C", "D", "E", "F"]

        def mock_get_clue(cat, val):
            return {"category": cat, "value": val, "question": "Q", "answer": "A"}

        board = game.generate_board(categories, mock_get_clue)

        result = game.mark_clue_answered(board, "INVALID", 200)
        assert result is False
