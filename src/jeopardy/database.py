"""
SQLite database operations for Jeopardy clues.

This module handles:
- Creating the database schema
- Loading clues into the database
- Querying clues for the game

Concepts practiced:
- SQL basics (notebook 11)
- sqlite3 module (notebook 11)
- Context managers (notebook 06)
- Error handling (notebook 06)

Why use a database?
- Fast queries on 200K+ clues
- Easy to find categories with enough clues at each value
- Random selection is built into SQL (ORDER BY RANDOM())
"""

import sqlite3
from pathlib import Path


# Default database location
DATABASE_PATH = Path(__file__).parent.parent.parent / "data" / "jeopardy.db"


def get_connection(db_path: Path = DATABASE_PATH) -> sqlite3.Connection:
    """
    Get a database connection.

    Args:
        db_path: Path to database file

    Returns:
        sqlite3.Connection object

    Note: The caller is responsible for closing this connection!
    Better to use create_database() and other functions that manage
    connections internally.
    """
    return sqlite3.connect(db_path)


def create_database(db_path: Path = DATABASE_PATH) -> None:
    """
    Create the Jeopardy database with the clues table.

    Schema:
        clues table:
        - id: INTEGER PRIMARY KEY AUTOINCREMENT
        - category: TEXT NOT NULL
        - value: INTEGER
        - question: TEXT NOT NULL
        - answer: TEXT NOT NULL
        - round: TEXT
        - show_number: INTEGER
        - air_date: TEXT

    Args:
        db_path: Where to create the database

    Example:
        >>> create_database(Path('test.db'))
        >>> # Now test.db exists with clues table

    Hint: Use CREATE TABLE IF NOT EXISTS

    Think about: Should we add any indexes? What queries will be common?
    (category and value lookups are frequent - indexes help!)
    """
    with sqlite3.connect(db_path) as conn:                                                                        
      conn.execute("CREATE TABLE IF NOT EXISTS clues (id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT NOT NULL, value INTEGER, question TEXT NOT NULL, answer TEXT NOT NULL, round TEXT NOT NULL, show_number INTEGER, air_date TEXT)")


def load_clues_to_db(
    clues: list[dict],
    db_path: Path = DATABASE_PATH,
    clear_existing: bool = True
) -> int:
    """
    Insert clues into the database.

    Args:
        clues: List of clue dictionaries
        db_path: Path to database file
        clear_existing: If True, delete existing clues first

    Returns:
        Number of clues inserted

    Example:
        >>> clues = [{'category': 'SCIENCE', 'value': 200, ...}]
        >>> count = load_clues_to_db(clues)
        >>> print(f"Loaded {count} clues")

    Hint: executemany() is more efficient than execute() in a loop

    IMPORTANT: Use parameterized queries (? placeholders), not f-strings!
    Bad:  f"INSERT INTO clues VALUES ('{clue['category']}')"  # SQL injection!
    Good: "INSERT INTO clues (category) VALUES (?)", (clue['category'],)
    """
    with sqlite3.connect(db_path) as conn:                                                                        
      if clear_existing:
        conn.execute("DELETE FROM clues")
      conn.executemany("INSERT INTO clues (category, value, question, answer, round, show_number, air_date) VALUES (?, ?, ?, ?, ?, ?, ?)", [(clue['category'], clue['value'], clue['question'], clue['answer'], clue['round'], clue['show_number'], clue['air_date']) for clue in clues])
      return len(clues)

def get_random_clue(
    category: str,
    value: int,
    db_path: Path = DATABASE_PATH,
    round_num: int | None = None
) -> dict | None:
    """
    Get a random clue from a category at a specific value.

    Args:
        category: Category name
        value: Dollar value (200, 400, 600, 800, 1000 for round 1; 400, 800, 1200, 1600, 2000 for round 2)
        db_path: Path to database
        round_num: Optional round filter (1 for Jeopardy, 2 for Double Jeopardy)

    Returns:
        Clue dictionary or None if no matching clue exists
    """
    with sqlite3.connect(db_path) as conn:
        if round_num is not None:
            row = conn.execute(
                "SELECT * FROM clues WHERE category = ? AND value = ? AND round = ? ORDER BY RANDOM() LIMIT 1",
                (category, value, str(round_num))
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT * FROM clues WHERE category = ? AND value = ? ORDER BY RANDOM() LIMIT 1",
                (category, value)
            ).fetchone()
        if row is None:
            return None
        columns = ["id", "category", "value", "question", "answer", "round", "show_number", "air_date"]
        return dict(zip(columns, row))


def get_usable_categories(
    min_clues_per_value: int = 1,
    db_path: Path = DATABASE_PATH,
    round_num: int = 1
) -> list[str]:
    """
    Find categories that have at least min_clues_per_value at each value level.

    Args:
        min_clues_per_value: Minimum clues needed at each value
        db_path: Path to database
        round_num: 1 for Jeopardy (200-1000), 2 for Double Jeopardy (400-2000)

    Returns:
        List of category names that are "complete" for a game board
    """
    if round_num == 1:
        values = (200, 400, 600, 800, 1000)
    else:
        values = (400, 800, 1200, 1600, 2000)

    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            f"""SELECT category FROM (
                SELECT category, value FROM clues
                WHERE value IN {values} AND round = ?
                GROUP BY category, value
                HAVING COUNT(*) >= ?
            ) GROUP BY category HAVING COUNT(*) = 5""",
            (str(round_num), min_clues_per_value)
        ).fetchall()
        return [row[0] for row in rows]


def get_final_jeopardy_clue(db_path: Path = DATABASE_PATH) -> dict | None:
    """
    Get a random Final Jeopardy clue.

    Returns:
        Clue dictionary with category, question, answer, or None if none found
    """
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM clues WHERE round = '3' ORDER BY RANDOM() LIMIT 1"
        ).fetchone()
        if row is None:
            return None
        columns = ["id", "category", "value", "question", "answer", "round", "show_number", "air_date"]
        return dict(zip(columns, row))


def count_clues_by_category(db_path: Path = DATABASE_PATH) -> dict[str, int]:
    """
    Count total clues in each category.

    Returns:
        Dictionary mapping category name to clue count

    Example:
        >>> counts = count_clues_by_category()
        >>> counts['SCIENCE']
        42

    SQL Hint: SELECT category, COUNT(*) ... GROUP BY category
    """
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute("SELECT category, COUNT(*) FROM clues GROUP BY category").fetchall()
        return {row[0]: row[1] for row in rows}


def get_category_value_counts(
    category: str,
    db_path: Path = DATABASE_PATH
) -> dict[int, int]:
    """
    Get clue counts at each value level for a category.

    Args:
        category: Category name

    Returns:
        Dictionary mapping value to count, e.g., {200: 3, 400: 5, ...}

    Example:
        >>> counts = get_category_value_counts('SCIENCE')
        >>> counts[400]  # How many $400 SCIENCE clues?
        5

    Useful for checking if a category can fill a game board column.
    """
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute("SELECT value, COUNT(*) FROM clues WHERE category = ? GROUP BY value", (category,)).fetchall()
        return {row[0]: row[1] for row in rows}


def get_total_clue_count(db_path: Path = DATABASE_PATH) -> int:
    """
    Get total number of clues in the database.

    Returns:
        Total clue count

    SQL: SELECT COUNT(*) FROM clues
    """
    with sqlite3.connect(db_path) as conn:
        row = conn.execute("SELECT COUNT(*) FROM clues").fetchone()
        return row[0]


def search_clues(
    search_term: str,
    db_path: Path = DATABASE_PATH,
    limit: int = 10
) -> list[dict]:
    """
    Search for clues containing a term in question or answer.

    Args:
        search_term: Text to search for
        db_path: Path to database
        limit: Maximum results to return

    Returns:
        List of matching clue dictionaries

    SQL Hint: Use LIKE with % wildcards for partial matching
    Example: WHERE question LIKE '%mars%' OR answer LIKE '%mars%'
    """
    pass
