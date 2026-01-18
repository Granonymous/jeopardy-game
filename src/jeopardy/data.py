"""
Data loading and cleaning for Jeopardy clues.

This module handles:
- Loading JSON data from files
- Validating and cleaning clue data
- Filtering to "usable" clues for the game

Concepts practiced:
- File I/O (notebook 06)
- JSON handling (notebook 06)
- Dictionaries (notebook 03)
- List comprehensions (notebook 04)
- Error handling (notebook 06)
"""

from pathlib import Path
import json
import csv
from datetime import date


# Path to sample data (relative to project root)
SAMPLE_DATA_PATH = Path(__file__).parent.parent.parent / "notebooks" / "data" / "sample_jeopardy.json"
TSV_DATA_PATH = Path(__file__).parent.parent.parent / "clues.tsv"

# Date when Jeopardy doubled clue values
VALUE_CHANGE_DATE = date(2001, 11, 26)


def load_tsv_data(filepath: Path = TSV_DATA_PATH) -> list[dict]:
    """
    Load Jeopardy clues from TSV file.

    Handles the November 2001 value doubling:
    - Games before Nov 26, 2001: values are doubled to match modern format
    - Games after: values used as-is

    Args:
        filepath: Path to TSV file

    Returns:
        List of clue dictionaries with keys:
        - category, value, question, answer, round, air_date
    """
    clues = []

    with open(filepath, encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')

        for row in reader:
            try:
                # Parse the air date
                air_date_str = row['air_date']
                year, month, day = map(int, air_date_str.split('-'))
                air_date = date(year, month, day)

                # Get the clue value
                value = int(row['clue_value']) if row['clue_value'] else 0

                # Double values for pre-2001 games
                if air_date < VALUE_CHANGE_DATE:
                    value = value * 2

                clue = {
                    'category': row['category'].strip().upper(),
                    'value': value,
                    'question': row['answer'].strip(),  # "answer" in TSV is the clue shown
                    'answer': row['question'].strip(),   # "question" in TSV is the response
                    'round': row['round'],
                    'air_date': air_date_str,
                    'show_number': 0  # Not in TSV
                }

                clues.append(clue)

            except (ValueError, KeyError):
                # Skip malformed rows
                continue

    return clues


def load_sample_data() -> list[dict]:
    """
    Load the sample Jeopardy data from notebooks/data/sample_jeopardy.json.

    Returns:
        List of clue dictionaries, each with keys:
        - category: str
        - value: int
        - question: str (the clue shown to contestants)
        - answer: str (the correct response)
        - round: str
        - show_number: int
        - air_date: str

    Raises:
        FileNotFoundError: If sample file doesn't exist

    Example:
        >>> clues = load_sample_data()
        >>> len(clues)
        70
        >>> clues[0]['category']
        'SCIENCE'

    Hint: Use pathlib and json.load() with a context manager
    """
    with open(SAMPLE_DATA_PATH) as f:
        data = json.load(f)
        
    return data 


def load_json_file(filepath: Path) -> list[dict]:
    """
    Load clue data from any JSON file.

    Args:
        filepath: Path to the JSON file

    Returns:
        List of clue dictionaries

    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file isn't valid JSON

    Hint: This is a more general version of load_sample_data
    """
    pass


def validate_clue(clue: dict) -> bool:
    """
    Check if a clue is valid and usable for the game.

    A valid clue has:
    - Non-empty category, question, and answer
    - A numeric value (200, 400, 600, 800, or 1000 for standard rounds)
    - No references to images/video/audio (text like "[video clue]")

    Args:
        clue: A clue dictionary

    Returns:
        True if clue is usable, False otherwise

    Example:
        >>> validate_clue({'category': 'SCIENCE', 'value': 400,
        ...                'question': 'This planet is red',
        ...                'answer': 'Mars'})
        True
        >>> validate_clue({'category': '', 'value': 400,
        ...                'question': 'Test', 'answer': 'Test'})
        False

    Think about: What text patterns indicate an unusable clue?
    Look for: [video clue], [audio clue], seen here, pictured here
    """



    bad_patterns = ["[video", "[audio", "seen here", "pictured here"]                                         

    if not clue["category"] or not clue["question"] or not clue["answer"] or not isinstance(clue["value"], int) or any(pattern in clue["question"].lower() for pattern in bad_patterns):
        return False
    return True


def clean_clues(clues: list[dict]) -> list[dict]:
    """
    Filter and clean a list of clues for game use.

    Args:
        clues: Raw clue list from data source

    Returns:
        Filtered list containing only valid, cleaned clues

    Example:
        >>> raw = [{'category': 'SCIENCE', ...}, {'category': '', ...}]
        >>> clean = clean_clues(raw)
        >>> len(clean) < len(raw)
        True

    Hint: Use validate_clue() and list comprehension
    """
    return [clue for clue in clues if validate_clue(clue)]
    


def get_categories(clues: list[dict]) -> list[str]:
    """
    Get unique category names from clues.

    Args:
        clues: List of clue dictionaries

    Returns:
        Sorted list of unique category names

    Example:
        >>> clues = [{'category': 'SCIENCE'}, {'category': 'HISTORY'},
        ...          {'category': 'SCIENCE'}]
        >>> get_categories(clues)
        ['HISTORY', 'SCIENCE']

    Hint: Sets are good for uniqueness, then convert to sorted list
    """
    return sorted(set(clue["category"] for clue in clues if validate_clue(clue)))


def filter_by_category(clues: list[dict], category: str) -> list[dict]:
    """
    Get all clues in a specific category.

    Args:
        clues: List of clue dictionaries
        category: Category name to filter by

    Returns:
        List of clues matching the category

    Example:
        >>> clues = [{'category': 'SCIENCE', 'value': 200},
        ...          {'category': 'HISTORY', 'value': 200}]
        >>> filter_by_category(clues, 'SCIENCE')
        [{'category': 'SCIENCE', 'value': 200}]
    """
    return [clue for clue in clues if clue["category"] == category]


def filter_by_value(clues: list[dict], value: int) -> list[dict]:
    """
    Get all clues at a specific dollar value.

    Args:
        clues: List of clue dictionaries
        value: Dollar value to filter by (200, 400, 600, 800, 1000)

    Returns:
        List of clues matching the value
    """
    pass


def get_clue_stats(clues: list[dict]) -> dict:
    """
    Get summary statistics about a list of clues.

    Returns a dictionary with:
    - total: Total number of clues
    - by_category: Dict mapping category -> count
    - by_value: Dict mapping value -> count
    - by_round: Dict mapping round -> count

    Args:
        clues: List of clue dictionaries

    Returns:
        Dictionary of statistics

    Useful for exploring the data before building the game.
    """
    pass
