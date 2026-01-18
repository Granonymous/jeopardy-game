#!/usr/bin/env python3
"""
Download the full Jeopardy dataset from Hugging Face.

This script downloads the jeopardy-datasets/jeopardy dataset and
saves it as JSON for use in the project.

Run with: uv run python scripts/download_data.py

The dataset contains ~216K questions with fields:
- category: str
- value: str (like "$400" - needs parsing!)
- question: str (the clue)
- answer: str (correct response)
- round: str
- show_number: str
- air_date: str

Requires: uv add datasets
"""

from pathlib import Path
import json
import re


def parse_value(value_str: str | None) -> int | None:
    """
    Parse a value string like "$400" to an integer 400.

    Args:
        value_str: String like "$400" or None

    Returns:
        Integer value or None if unparseable

    Examples:
        >>> parse_value("$400")
        400
        >>> parse_value("$1,000")
        1000
        >>> parse_value(None)
        None
    """
    if not value_str:
        return None

    # Remove $ and commas, then convert to int
    try:
        cleaned = value_str.replace("$", "").replace(",", "")
        return int(cleaned)
    except (ValueError, AttributeError):
        return None


def download_jeopardy_data(output_path: Path) -> int:
    """
    Download Jeopardy data from Hugging Face and save as JSON.

    Args:
        output_path: Where to save the JSON file

    Returns:
        Number of questions downloaded
    """
    try:
        from datasets import load_dataset
    except ImportError:
        print("Error: 'datasets' package not installed.")
        print("Install with: uv add datasets")
        print("Or: pip install datasets")
        return 0

    print("Downloading dataset from Hugging Face...")
    print("(This may take a minute on first run)")

    # Load the dataset
    ds = load_dataset("jeopardy-datasets/jeopardy")

    # Convert to list of dicts
    clues = []
    for item in ds["train"]:
        clue = {
            "category": item.get("category", ""),
            "value": parse_value(item.get("value")),
            "question": item.get("question", ""),
            "answer": item.get("answer", ""),
            "round": item.get("round", ""),
            "show_number": item.get("show_number"),
            "air_date": item.get("air_date", ""),
        }
        clues.append(clue)

    # Save to JSON
    print(f"Writing {len(clues):,} clues to {output_path}...")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(clues, f, indent=2)

    print("Done!")
    return len(clues)


def main():
    """Main entry point."""
    output_path = Path(__file__).parent.parent / "data" / "jeopardy_full.json"

    print("=" * 50)
    print("Jeopardy Dataset Downloader")
    print("=" * 50)
    print()

    count = download_jeopardy_data(output_path)

    if count > 0:
        print()
        print(f"Success! Downloaded {count:,} questions.")
        print(f"Saved to: {output_path}")
        print()
        print("You can now load this data with:")
        print("  from jeopardy.data import load_json_file")
        print(f"  clues = load_json_file(Path('{output_path}'))")


if __name__ == "__main__":
    main()
