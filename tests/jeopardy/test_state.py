"""
Tests for jeopardy.state module.

Tests for game state management and persistence.

Run with: uv run pytest tests/jeopardy/test_state.py -v
"""

import pytest
import json
from pathlib import Path

from jeopardy.state import GameState, save_game, load_game, create_new_game


class TestGameState:
    """Tests for GameState dataclass."""

    def test_initial_score_is_zero(self):
        """New game should start with score 0."""
        state = GameState()
        assert state.score == 0

    def test_initial_answered_is_empty(self):
        """New game should have no answered clues."""
        state = GameState()
        assert len(state.answered) == 0

    def test_initial_game_not_over(self):
        """New game should not be over."""
        state = GameState()
        assert state.game_over is False

    def test_select_clue_sets_current(self):
        """select_clue should set current_clue."""
        state = GameState(categories=["SCIENCE"])
        clue = {"question": "Test", "answer": "Test"}

        state.select_clue("SCIENCE", 400, clue)

        assert state.current_clue is not None
        assert state.current_clue["question"] == "Test"

    def test_select_already_answered_raises(self):
        """Selecting an already answered clue should raise ValueError."""
        state = GameState(categories=["SCIENCE"])
        state.answered.add(("SCIENCE", 400))

        clue = {"question": "Test", "answer": "Test"}

        with pytest.raises(ValueError):
            state.select_clue("SCIENCE", 400, clue)

    def test_answer_clue_correct_adds_score(self):
        """Correct answer should add to score."""
        state = GameState(categories=["SCIENCE"])
        clue = {"question": "Test", "answer": "Test"}
        state.select_clue("SCIENCE", 400, clue)

        state.answer_clue(correct=True, value=400)

        assert state.score == 400

    def test_answer_clue_incorrect_subtracts_score(self):
        """Incorrect answer should subtract from score."""
        state = GameState(categories=["SCIENCE"])
        clue = {"question": "Test", "answer": "Test"}
        state.select_clue("SCIENCE", 400, clue)

        state.answer_clue(correct=False, value=400)

        assert state.score == -400

    def test_answer_clue_marks_answered(self):
        """Answering should mark clue as answered."""
        state = GameState(categories=["SCIENCE"])
        clue = {"question": "Test", "answer": "Test", "category": "SCIENCE", "value": 400}
        state.select_clue("SCIENCE", 400, clue)

        state.answer_clue(correct=True, value=400)

        assert state.is_answered("SCIENCE", 400)

    def test_answer_clue_clears_current(self):
        """Answering should clear current_clue."""
        state = GameState(categories=["SCIENCE"])
        clue = {"question": "Test", "answer": "Test", "category": "SCIENCE", "value": 400}
        state.select_clue("SCIENCE", 400, clue)

        state.answer_clue(correct=True, value=400)

        assert state.current_clue is None

    def test_is_answered(self):
        """is_answered should return correct status."""
        state = GameState()
        state.answered.add(("SCIENCE", 400))

        assert state.is_answered("SCIENCE", 400) is True
        assert state.is_answered("SCIENCE", 200) is False
        assert state.is_answered("HISTORY", 400) is False

    def test_remaining_clues_count(self):
        """remaining_clues_count should be correct."""
        state = GameState(categories=["A", "B", "C", "D", "E", "F"])

        # 6 categories * 5 values = 30 total
        assert state.remaining_clues_count() == 30

        # Answer one
        state.answered.add(("A", 200))
        assert state.remaining_clues_count() == 29

    def test_get_available_values(self):
        """get_available_values should return unanswered values."""
        state = GameState(categories=["SCIENCE"])

        # All available initially
        available = state.get_available_values("SCIENCE")
        assert 200 in available
        assert 400 in available

        # Answer one
        state.answered.add(("SCIENCE", 400))
        available = state.get_available_values("SCIENCE")
        assert 200 in available
        assert 400 not in available


class TestSaveLoadGame:
    """Tests for game persistence."""

    def test_save_creates_file(self, tmp_path):
        """save_game should create a JSON file."""
        filepath = tmp_path / "save.json"
        state = GameState(score=500)

        save_game(state, filepath)

        assert filepath.exists()

    def test_load_restores_score(self, tmp_path):
        """load_game should restore the score."""
        filepath = tmp_path / "save.json"
        state = GameState(score=500)
        save_game(state, filepath)

        loaded = load_game(filepath)

        assert loaded.score == 500

    def test_load_restores_answered(self, tmp_path):
        """load_game should restore answered clues."""
        filepath = tmp_path / "save.json"
        state = GameState()
        state.answered.add(("SCIENCE", 400))
        state.answered.add(("HISTORY", 200))
        save_game(state, filepath)

        loaded = load_game(filepath)

        assert ("SCIENCE", 400) in loaded.answered
        assert ("HISTORY", 200) in loaded.answered

    def test_load_restores_categories(self, tmp_path):
        """load_game should restore categories."""
        filepath = tmp_path / "save.json"
        state = GameState(categories=["A", "B", "C", "D", "E", "F"])
        save_game(state, filepath)

        loaded = load_game(filepath)

        assert loaded.categories == ["A", "B", "C", "D", "E", "F"]

    def test_load_nonexistent_raises(self, tmp_path):
        """load_game should raise FileNotFoundError for missing file."""
        filepath = tmp_path / "nonexistent.json"

        with pytest.raises(FileNotFoundError):
            load_game(filepath)

    def test_round_trip(self, tmp_path):
        """Save then load should preserve all state."""
        filepath = tmp_path / "save.json"

        original = GameState(
            score=1200,
            categories=["A", "B", "C", "D", "E", "F"],
            game_over=False
        )
        original.answered.add(("A", 200))
        original.answered.add(("B", 400))

        save_game(original, filepath)
        loaded = load_game(filepath)

        assert loaded.score == original.score
        assert loaded.answered == original.answered
        assert loaded.categories == original.categories
        assert loaded.game_over == original.game_over


class TestCreateNewGame:
    """Tests for creating new games."""

    def test_creates_with_categories(self):
        """Should create state with given categories."""
        categories = ["A", "B", "C", "D", "E", "F"]

        state = create_new_game(categories)

        assert state.categories == categories

    def test_starts_fresh(self):
        """New game should have zero score and no answered clues."""
        categories = ["A", "B", "C", "D", "E", "F"]

        state = create_new_game(categories)

        assert state.score == 0
        assert len(state.answered) == 0

    def test_rejects_wrong_category_count(self):
        """Should raise ValueError if not 6 categories."""
        with pytest.raises(ValueError):
            create_new_game(["A", "B", "C"])  # Only 3

        with pytest.raises(ValueError):
            create_new_game(["A", "B", "C", "D", "E", "F", "G"])  # 7
