"""
Core game logic for Jeopardy.

This module contains PURE FUNCTIONS for game mechanics:
- Board generation
- Answer checking
- Scoring

Pure functions have no side effects - they just compute results.
This makes them easy to test and reason about.

Concepts practiced:
- Functions (notebook 05)
- Dictionaries for state (notebook 03)
- String processing (notebook 02)
- Control flow (notebook 04)
- Type hints (notebook 05)
"""

from typing import TypedDict, Callable
from rapidfuzz import fuzz

class Clue(TypedDict):
    """A single Jeopardy clue."""
    category: str
    value: int
    question: str  # The clue shown to players (yes, Jeopardy calls this "question")
    answer: str    # The correct response


class BoardSlot(TypedDict):
    """A slot on the game board."""
    clue: Clue
    answered: bool


# Type alias for the game board
# Board maps: category -> value -> BoardSlot
Board = dict[str, dict[int, BoardSlot]]

# Standard Jeopardy values
STANDARD_VALUES = [200, 400, 600, 800, 1000]
DOUBLE_JEOPARDY_VALUES = [400, 800, 1200, 1600, 2000]


def normalize_answer(answer: str) -> str:
    """
    Normalize an answer for comparison.

    Normalization should:
    - Convert to lowercase
    - Strip leading/trailing whitespace
    - Remove common prefixes: "what is", "who is", "what are", "who are"
    - Remove punctuation (periods, question marks, etc.)
    - Optionally handle "the" at the beginning

    Args:
        answer: Raw answer string

    Returns:
        Normalized answer for comparison

    Examples:
        >>> normalize_answer("What is Mars?")
        'mars'
        >>> normalize_answer("WHO IS Einstein")
        'einstein'
        >>> normalize_answer("  The Beatles  ")
        'beatles'  # or 'the beatles' - your choice on handling "the"
        >>> normalize_answer("George Washington")
        'george washington'

    Think about:
    - What variations should definitely match?
    - Use string methods: .lower(), .strip(), .startswith(), .replace()
    - The `re` module can help with punctuation removal
    """
    prefixes = ["what is ", "who is ", "what are ", "who are ", "the ", "a ", "an ", "what's ", "whats ", "who's ", "whos "]
    sufixes = [".", "?", "!", ",", ";", ":"]
    result = answer.lower().strip()
    for prefix in prefixes:
        result = result.removeprefix(prefix).strip()
    for sufix in sufixes:
        result = result.replace(sufix, "")
    return result


def check_answer(player_answer: str, correct_answer: str) -> bool:
    """
    Check if player's answer matches the correct answer.

    Uses normalize_answer() on both inputs before comparing.

    Args:
        player_answer: What the player typed
        correct_answer: The correct response from the clue

    Returns:
        True if answers match (after normalization), False otherwise

    Examples:
        >>> check_answer("What is Mars?", "Mars")
        True
        >>> check_answer("mars", "Mars")
        True
        >>> check_answer("Jupiter", "Mars")
        False

    Future enhancement: Could add fuzzy matching for close answers
    (e.g., "Shakespear" vs "Shakespeare")
    """
    # Normalize both answers first
    player_norm = normalize_answer(player_answer)
    correct_norm = normalize_answer(correct_answer)

    if player_norm == correct_norm:
        return True
    if fuzz.ratio(player_norm, correct_norm) >= 80:
        return True
    if fuzz.partial_ratio(player_norm, correct_norm) >= 90:
        return True
    return False


def calculate_score_change(value: int, correct: bool) -> int:
    """
    Calculate how the score changes based on answer correctness.

    In Jeopardy:
    - Correct answer: +value
    - Incorrect answer: -value

    Args:
        value: The clue's dollar value
        correct: Whether the answer was correct

    Returns:
        Score change (positive or negative)

    Examples:
        >>> calculate_score_change(400, True)
        400
        >>> calculate_score_change(400, False)
        -400
    """
    if (correct):
        return +value
    return -value


def generate_board(
    categories: list[str],
    get_clue_fn: Callable[[str, int], Clue | None],
    values: list[int] | None = None
) -> Board:
    """
    Generate a new Jeopardy game board.

    Args:
        categories: List of 6 category names
        get_clue_fn: Function that takes (category, value) and returns a Clue
                     (This will typically be database.get_random_clue)
        values: List of dollar values to use (defaults to STANDARD_VALUES)

    Returns:
        Board structure with all clues loaded

    Raises:
        ValueError: If not exactly 6 categories provided
    """
    if len(categories) != 6:
        raise ValueError("Exactly 6 categories are required to generate the board.")

    if values is None:
        values = STANDARD_VALUES

    board = {}
    for category in categories:
        board[category] = {}
        for value in values:
            clue = get_clue_fn(category, value)
            if clue is not None:
                board[category][value] = {'clue': clue, 'answered': False}
            else:
                board[category][value] = {'clue': None, 'answered': False}
    return board


def is_board_complete(board: Board) -> bool:
    """
    Check if all clues on the board have been answered.

    Args:
        board: The game board

    Returns:
        True if all slots are answered, False otherwise

    Example:
        >>> board = generate_board(categories, get_clue_fn)
        >>> is_board_complete(board)
        False
        >>> # ... play game, answer all clues ...
        >>> is_board_complete(board)
        True
    """
    for category_slots in board.values():
        for slot in category_slots.values():
            if not slot['answered']:
                return False
    return True


def get_remaining_clues(board: Board) -> list[tuple[str, int]]:
    """
    Get list of (category, value) pairs that haven't been answered.

    Args:
        board: The game board

    Returns:
        List of (category, value) tuples for unanswered clues

    Example:
        >>> remaining = get_remaining_clues(board)
        >>> remaining[0]
        ('SCIENCE', 200)

    Useful for: displaying available selections, checking if game is over
    """
    remaining = []
    for category, category_slots in board.items():
        for value, slot in category_slots.items():
            if not slot['answered']:
                remaining.append((category, value))
    return remaining


def get_clue_from_board(board: Board, category: str, value: int) -> Clue | None:
    """
    Get a specific clue from the board.

    Args:
        board: The game board
        category: Category name
        value: Dollar value

    Returns:
        The Clue dict, or None if not found or already answered
    """
    if category in board and value in board[category]:
        slot = board[category][value]
        if not slot['answered']:
            return slot['clue']
    return None


def mark_clue_answered(board: Board, category: str, value: int) -> bool:
    """
    Mark a clue as answered on the board.

    Args:
        board: The game board (modified in place)
        category: Category name
        value: Dollar value

    Returns:
        True if successfully marked, False if not found

    Note: This modifies the board in place. In a more functional style,
    you'd return a new board, but mutation is clearer for beginners.
    """
    if category not in board or value not in board[category]:
        return False
    board[category][value]['answered'] = True
    return True
    


def count_remaining(board: Board) -> int:
    """
    Count how many clues remain unanswered.

    Args:
        board: The game board

    Returns:
        Number of unanswered clues
    """
    return len(get_remaining_clues(board))
