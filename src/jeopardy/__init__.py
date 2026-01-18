"""
Jeopardy! Game - A Python learning project.

This package implements a playable Jeopardy game using real clues.
Built incrementally as part of learning Python fundamentals.

NOTE FOR STUDENTS:
==================
All functions in this package are STUBS (they just have `pass`).
YOU implement them! This is the learning exercise.

Start with data.py, then database.py, then game.py, etc.
Use `pylearn` to test your implementations as you go.
Run `uv run pytest tests/jeopardy/` to check if your code works.

Tests will FAIL until you implement the functions - that's expected!

Modules:
    data: Load and clean Jeopardy clue data
    database: SQLite storage and queries
    game: Core game logic (pure functions)
    state: Game state management
    cli: Command-line interface
"""

__version__ = "0.1.0"

# Exports will be added as modules are implemented
# Example (uncomment as you build):
# from .data import load_sample_data, clean_clues
# from .game import check_answer, generate_board
# from .cli import play_game
