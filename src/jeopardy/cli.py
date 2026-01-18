"""
Command-line interface for the Jeopardy game.

This module handles:
- Displaying the game board
- Getting player input
- Running the main game loop

Concepts practiced:
- User input handling (new!)
- Game loops (new!)
- String formatting (notebook 02)
- Control flow (notebook 04)

Design note:
The CLI is separate from game logic so we could later add
a web UI (Streamlit) or other interface without changing the core game.
"""

import os
import random
from pathlib import Path

from .database import get_random_clue, get_usable_categories, create_database, load_clues_to_db
from .data import clean_clues, load_tsv_data
from .game import Board, STANDARD_VALUES, check_answer, calculate_score_change, generate_board
from .state import GameState, create_new_game


def clear_screen() -> None:
    """
    Clear the terminal screen.

    Works on both Windows and Unix-like systems.

    Hint: Use os.system('cls' or 'clear')
    """
    os.system('cls' if os.name == 'nt' else 'clear')


def display_welcome() -> None:
    """
    Display welcome message and instructions.

    Called at the start of a new game.
    """
    print("=" * 40)
    print("      WELCOME TO JEOPARDY!")
    print("=" * 40)
    print()

def display_board(
    categories: list[str],
    answered: set[tuple[str, int]],
    values: list[int] = STANDARD_VALUES
) -> None:
    """
    Print the game board to the terminal.

    Shows categories as columns, values as rows.
    Answered clues show as "-" or blank.
    Unanswered show as "$XXX".

    Example output:

        SCIENCE     HISTORY     SPORTS      MOVIES      FOOD        WORDS
        $200        $200        -           $200        -           $200
        $400        -           $400        -           $400        -
        $600        $600        $600        $600        $600        $600
        $800        $800        $800        $800        $800        $800
        $1000       $1000       $1000       $1000       $1000       $1000

    Args:
        categories: List of 6 category names
        answered: Set of (category, value) pairs already answered
        values: List of dollar values (rows)

    Hint: f-strings with width specifiers help alignment:
        f"{text:^15}"  # Center in 15 chars
        f"{text:<15}"  # Left align in 15 chars
    """
    for cat in categories:
        print(f"{cat:^12}", end="")
    print()
    for value in values:
        for cat in categories:
            if (cat, value) in answered:
                print(f"{'-':^12}", end="")
            else:
                print(f"${value:<11}", end="")
        print()


def display_score(score: int) -> None:
    """
    Display current score.

    Args:
        score: Current score (can be negative)

    Example:
        >>> display_score(1200)
        Score: $1,200
        >>> display_score(-400)
        Score: -$400
    """
    print(f"Score: ${score:,}" if score >= 0 else f"Score: -${-score:,}")


def display_clue(category: str, value: int, question: str) -> None:
    """
    Display a clue to the player.

    Args:
        category: The clue's category
        value: The dollar value
        question: The clue text

    Example output:

        SCIENCE for $400
        ════════════════════════════════════════
        "This planet appears red due to iron oxide on its surface"
        ════════════════════════════════════════
    """
    print(f"\n{category} for ${value}")
    print("═" * 40)
    print(f"{question}")
    print("═" * 40)


def get_category_selection(
    categories: list[str],
    answered: set[tuple[str, int]]
) -> str | None:
    """
    Prompt player to select a category.

    Shows numbered list of categories that still have available clues.
    Returns None if player wants to quit.

    Args:
        categories: All category names
        answered: Set of answered (category, value) pairs

    Returns:
        Selected category name, or None if quitting

    Example interaction:
        Select a category:
        1. SCIENCE
        2. HISTORY
        3. SPORTS
        > 1

    Hint:
    - Use input() in a while loop until valid
    - Handle 'q' or 'quit' to exit
    - Validate the number is in range
    """
    available = []
    for cat in categories:
        for value in STANDARD_VALUES:
            if (cat, value) not in answered:
                available.append(cat)
                break

    print("\nSelect a category:")
    for i, cat in enumerate(available, 1):
        print(f"{i}. {cat}")
    print(" Press q to quit")

    while True:
        choice = input("> ").strip().lower()
        if choice in ('q', 'quit'):
            return None
        try:
            num = int(choice)
            if 1 <= num <= len(available):
                return available[num - 1]
        except ValueError:
            pass
        print("Invalid selection. Please try again.")


def get_value_selection(
    category: str,
    available_values: list[int]
) -> int | None:
    """
    Prompt player to select a dollar value.

    Args:
        category: Selected category (for display)
        available_values: Values still available in this category

    Returns:
        Selected dollar value, or None if going back/quitting

    Example interaction:
        SCIENCE - Select a value:
        $200  $400  $600
        > 400
    """
    print(f"\n{category} - Select a value:")
    print("   " + "   ".join(f"${v}" for v in available_values))
    print(" Press b to go back, q to quit")

    while True:
        choice = input("> ").strip().lower()
        if choice in ('q', 'quit'):
            return None
        if choice in ('b', 'back'):
            return None
        try:
            value = int(choice)
            if value in available_values:
                return value
        except ValueError:
            pass
        print("Invalid selection. Please try again.")



def get_player_answer() -> str | None:
    """
    Prompt player for their answer to the current clue.

    Returns:
        Player's answer (raw input), or None if they pass

    Handle special inputs:
    - Empty string or 'pass' -> return None (no answer)
    - 'q' or 'quit' -> could raise an exception or return special value
    """
    answer = input("Your answer (or 'pass' to skip): ").strip()
    if answer.lower() in ('pass', 'p'):
        return None
    return answer


def display_result(
    correct: bool,
    correct_answer: str,
    score_change: int,
    new_score: int
) -> None:
    """
    Display whether the answer was correct and score change.

    Args:
        correct: Whether the answer was correct
        correct_answer: The actual correct answer
        score_change: How much the score changed
        new_score: The new total score

    Example (correct):
        Correct! +$400
        Score: $1,600

    Example (incorrect):
        Sorry! The answer was: Mars
        -$400
        Score: $800
    """
    if correct:
        print(f"Correct! +${score_change}")
    else:
        print(f"Sorry! The answer was: {correct_answer}")
        print(f"-${-score_change}")
    print(f"Score: ${new_score:,}" if new_score >= 0 else f"Score: -${-new_score:,}")


def display_game_over(final_score: int, clues_answered: int) -> None:
    """
    Display end-of-game message with final score.

    Args:
        final_score: Player's final score
        clues_answered: How many clues they answered

    Example:
        ════════════════════════════════════════
        GAME OVER!

        Final Score: $2,400
        Clues Answered: 18/30
        ════════════════════════════════════════
    """
    print("\n" + "=" * 40)
    print("         GAME OVER!")
    print(f"\n  Final Score: ${final_score:,}")
    print(f"  Clues Answered: {clues_answered}/30")
    print("=" * 40)

def confirm_quit() -> bool:
    """
    Ask player to confirm they want to quit.

    Returns:
        True if they confirm quit, False to continue
    """
    answer = input("Really quit? (y/n): ").strip().lower()
    return answer in ('y', 'yes')

def play_game() -> None:
    """
    Main game loop.

    This ties everything together:
    1. Initialize database connection
    2. Select 6 random usable categories
    3. Generate a game board
    4. Create initial game state
    5. Loop until board complete or player quits:
        a. Clear screen and show board
        b. Show current score
        c. Get category selection
        d. Get value selection
        e. Display the clue
        f. Get player's answer
        g. Check answer and update score
        h. Mark clue as answered
        i. Check if game over (all clues answered)
    6. Display final results

    This is the function called when running the game!

    The game loop pattern:
    ```
    while not game_over:
        display_current_state()
        action = get_player_action()
        if action is quit:
            break
        process_action(action)
        update_state()
        game_over = check_end_condition()
    show_final_results()
    ```
    """
    db_path = Path("jeopardy.db")

    if not db_path.exists():                                                                                  
          print("Setting up database for first run...")
          print("Loading clues from TSV (this may take a moment)...")
          create_database(db_path)
          raw_clues = load_tsv_data()
          clues = clean_clues(raw_clues)
          load_clues_to_db(clues, db_path)
          print(f"Loaded {len(clues)} clues!")

    all_categories = get_usable_categories(db_path=db_path)
    categories = random.sample(all_categories, 6)

    def get_clue(category: str, value: int):
        return get_random_clue(category, value, db_path)
    
    board = generate_board(categories, get_clue)

    state = create_new_game(categories)

    while True:
        clear_screen()
        display_board(categories, state.answered)
        display_score(state.score)

        category = get_category_selection(categories, state.answered)
        if category is None:
            if confirm_quit():
                break
            else:
                continue

        available_values = [v for v in STANDARD_VALUES if (category, v) not in state.answered]
        value = get_value_selection(category, available_values)
        if value is None:
            continue

        clue = board[category][value]['clue']
        display_clue(category, value, clue['question'])

        player_answer = get_player_answer()
        if player_answer is None:
            state.answered.add((category, value))
            continue

        correct = check_answer(player_answer, clue['answer'])
        score_change = calculate_score_change(value, correct)
        state.select_clue(category, value, clue)
        state.answer_clue(correct, value)

        display_result(correct, clue['answer'], score_change, state.score)
        input("Press Enter to continue...")
        
        if state.remaining_clues_count() == 0:
            break

    display_game_over(state.score, len(state.answered))

# Entry point when running as script
if __name__ == "__main__":
    print("Welcome to Jeopardy!")
    print("Starting game...")
    play_game()
