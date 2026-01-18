"""
Game state management.

This module handles:
- Tracking game progress (score, answered clues)
- Saving and loading game state
- Game session management

Concepts practiced:
- Dataclasses (notebook 10)
- JSON serialization (notebook 06)
- State management (new concept!)

Why separate state from logic?
- Game logic functions stay pure (easy to test)
- State changes are explicit and trackable
- Can save/load games easily
"""

from dataclasses import dataclass, field, asdict
from pathlib import Path
import json
from typing import Any


@dataclass
class GameState:
    """
    Represents the current state of a Jeopardy game.

    This tracks everything we need to know about an in-progress game.

    Attributes:
        score: Current player score (can be negative!)
        answered: Set of (category, value) tuples for clues already answered
        current_clue: The currently active clue being answered, if any
        categories: The 6 categories in this game
        game_over: Whether the game has ended

    Example:
        >>> state = GameState()
        >>> state.score
        0
        >>> state.select_clue('SCIENCE', 400, {'question': '...', 'answer': '...'})
        >>> state.answer_clue(correct=True, value=400)
        >>> state.score
        400
    """
    score: int = 0
    answered: set[tuple[str, int]] = field(default_factory=set)
    current_clue: dict | None = None
    categories: list[str] = field(default_factory=list)
    game_over: bool = False

    def select_clue(self, category: str, value: int, clue: dict) -> None:
        """
        Mark a clue as the current active clue.

        Called when player selects a clue from the board.

        Args:
            category: Category of selected clue
            value: Value of selected clue
            clue: The clue dictionary

        Raises:
            ValueError: If clue was already answered

        Example:
            >>> state.select_clue('SCIENCE', 400, {'question': 'Red planet', 'answer': 'Mars'})
            >>> state.current_clue['question']
            'Red planet'
        """
        if self.is_answered(category, value):
            raise ValueError("Clue already answered")
        self.current_clue = {**clue, "category": category, "value": value}
    

    def answer_clue(self, correct: bool, value: int) -> None:
        """
        Record the result of answering the current clue.

        Updates score and marks clue as answered.
        Clears current_clue after recording.

        Args:
            correct: Whether the answer was correct
            value: The value of the answered clue

        Example:
            >>> state.answer_clue(correct=True, value=400)
            >>> state.score
            400
        """
        if self.current_clue is None:
            raise ValueError("No current clue to answer")
        if correct:
            self.score += value
        else:
            self.score -= value
        self.answered.add((self.current_clue['category'], self.current_clue['value']))
        self.current_clue = None

    def is_answered(self, category: str, value: int) -> bool:
        """
        Check if a specific clue has been answered.

        Args:
            category: Category name
            value: Dollar value

        Returns:
            True if already answered, False if still available
        """
        return (category, value) in self.answered

    def remaining_clues_count(self) -> int:
        """
        Count how many clues are left on the board.

        A standard board has 6 categories * 5 values = 30 clues.

        Returns:
            Number of unanswered clues
        """
        return 30 - len(self.answered)

    def get_available_values(self, category: str) -> list[int]:
        """
        Get values that haven't been answered in a category.

        Args:
            category: Category name

        Returns:
            List of available dollar values

        Example:
            >>> state.get_available_values('SCIENCE')
            [200, 400, 600, 800, 1000]  # All available at start
        """
        all_values = [200, 400, 600, 800, 1000]
        return [value for value in all_values if (category, value) not in self.answered]


def state_to_dict(state: GameState) -> dict[str, Any]:
    """
    Convert GameState to a JSON-serializable dictionary.

    Note: Sets aren't JSON serializable, so we convert to lists.

    Args:
        state: GameState to convert

    Returns:
        Dictionary that can be passed to json.dumps()

    Example:
        >>> state = GameState(score=400, answered={('SCIENCE', 400)})
        >>> d = state_to_dict(state)
        >>> d['answered']
        [['SCIENCE', 400]]  # List of lists, not set of tuples
    """
    data = asdict(state)
    data['answered'] = [list(item) for item in state.answered]
    return data


def dict_to_state(data: dict[str, Any]) -> GameState:
    """
    Convert dictionary back to GameState.

    Inverse of state_to_dict.

    Args:
        data: Dictionary from JSON

    Returns:
        Reconstructed GameState
    """
    answered_set = set((item[0], item[1]) for item in data['answered'])
    return GameState(
        score=data['score'],
        answered=answered_set,
        current_clue=data['current_clue'],
        categories=data['categories'],
        game_over=data['game_over']
    )


def save_game(state: GameState, filepath: Path) -> None:
    """
    Save game state to a JSON file.

    Args:
        state: Current game state
        filepath: Where to save

    Example:
        >>> save_game(state, Path('saved_game.json'))

    Hint: Use state_to_dict() then json.dump()
    """
    state_to_dict(state)
    with open(filepath, 'w') as f:
        json.dump(state_to_dict(state), f)


def load_game(filepath: Path) -> GameState:
    """
    Load game state from a JSON file.

    Args:
        filepath: Path to saved game

    Returns:
        Restored GameState

    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file isn't valid JSON

    Example:
        >>> state = load_game(Path('saved_game.json'))
        >>> state.score
        1200
    """
    with open(filepath, 'r') as f:
        data = json.load(f)
    return dict_to_state(data)


def create_new_game(categories: list[str]) -> GameState:
    """
    Create a fresh game state with given categories.

    Args:
        categories: List of 6 category names for this game

    Returns:
        New GameState ready to play

    Raises:
        ValueError: If not exactly 6 categories
    """
    if len(categories) != 6:
        raise ValueError("Exactly 6 categories are required to start a new game.")
    return GameState(categories=categories)
