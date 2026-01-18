# Jeopardy! Game

A fully playable Jeopardy! game built in Python, featuring over 216,000 real clues from the show's history. The game includes all three rounds (Jeopardy!, Double Jeopardy!, and Final Jeopardy!), complete with Daily Doubles, wagering mechanics, and fuzzy answer matching.

**Play it now:** [jeopardy-game.streamlit.app](https://granonymous-jeopardy-game.streamlit.app)

## Project Overview

This project was developed as part of my journey learning Python, with Claude serving as an AI tutor. While Claude guided me through concepts and helped debug issues, I implemented all the core functions myself. The project gave me hands-on experience with file I/O, SQL databases, object-oriented programming, web interfaces, and software architecture.

The game loads clue data from a TSV file containing historical Jeopardy! questions, stores them in a SQLite database for efficient querying, and presents them through either a command-line interface or a Streamlit web application. Players can answer questions using natural language, and the game uses fuzzy string matching to accept reasonable variations of correct answers.

## Project Structure

The codebase is organized into six Python modules, each handling a distinct responsibility:

### `data.py` — Data Loading and Cleaning

This module handles loading raw clue data from TSV files and preparing it for use. The `load_tsv_data()` function reads the historical clue dataset and handles a quirk of Jeopardy! history: before November 2001, clue values were half what they are today ($100-$500 instead of $200-$1000). The module automatically doubles pre-2001 values to normalize the dataset. The `validate_clue()` function filters out unusable clues—those referencing images, videos, or audio that wouldn't work in a text-based game. I learned about context managers for file handling and list comprehensions for data filtering while building this module.

### `database.py` — SQLite Database Operations

Rather than keeping 216,000+ clues in memory, this module manages a SQLite database for efficient storage and querying. The `create_database()` function sets up the schema, while `load_clues_to_db()` efficiently bulk-inserts clues using parameterized queries to prevent SQL injection. The `get_usable_categories()` function contains the most complex SQL query in the project—it finds categories that have at least one clue at each of the five value levels, ensuring every column on the game board can be fully populated. I chose SQLite over alternatives because it requires no server setup and stores everything in a single portable file.

### `game.py` — Core Game Logic

This module contains pure functions for game mechanics—functions with no side effects that simply compute results from their inputs. The `normalize_answer()` function strips common prefixes like "What is" and "Who are," removes punctuation, and lowercases text for comparison. The `check_answer()` function uses the RapidFuzz library for fuzzy string matching, accepting answers that are close enough to correct (handling typos like "Shakespear" vs "Shakespeare" or pluralization like "combs" vs "comb"). I debated how lenient to make the matching and settled on an 80% threshold for exact ratio matching and 90% for partial matching, which feels fair without being too forgiving.

### `state.py` — Game State Management

This module defines a `GameState` dataclass that tracks everything about an in-progress game: the current score, which clues have been answered, and the active categories. I separated state from logic so that the game logic functions could remain pure and easily testable. The module also handles serialization—converting the game state to and from JSON for save/load functionality. One challenge was that Python sets aren't JSON-serializable, so I had to convert them to lists of lists when saving and reconstruct them when loading.

### `cli.py` — Command-Line Interface

The CLI module provides a terminal-based way to play the game. It handles displaying the game board with proper column alignment, prompting for user input, validating selections, and running the main game loop. The game loop pattern—display state, get input, process action, update state, check for game over—was a new concept for me and appears throughout interactive applications.

### `web.py` — Streamlit Web Interface

The web interface provides a more accessible way to play, deployable to the cloud so anyone with a browser can join. It implements all three Jeopardy! rounds including Daily Doubles with wagering mechanics. When you hit a Daily Double, you can wager anywhere from $5 up to your current score (or the highest value on the board, whichever is greater). The interface includes skip buttons in the sidebar for jumping directly to Double Jeopardy or Final Jeopardy, useful for testing or quick games. One design challenge was managing Streamlit's session state across page reruns—every button click reruns the entire script, so all game state must be explicitly stored and retrieved.

## Design Decisions

**Fuzzy Matching:** I chose to implement fuzzy answer matching rather than requiring exact answers because real Jeopardy! accepts reasonable variations. The thresholds (80% ratio, 90% partial) were tuned through trial and error to feel fair.

**Database vs. In-Memory:** With 216,000+ clues, loading everything into memory would be wasteful. SQLite queries are fast and let me find categories with complete clue sets efficiently.

**Compressed Database for Deployment:** The SQLite database is 72MB uncompressed—too large for GitHub. I compress it to 33MB with gzip and decompress on first run in the cloud, avoiding the need for Git LFS.

**Separate Modules:** Keeping data loading, database operations, game logic, state management, and UI in separate files makes the code easier to test and modify. I can swap the CLI for a web interface without touching the game logic.

## Running Locally

```bash
uv sync
uv run streamlit run src/jeopardy/web.py
```

Or for the CLI version:
```bash
uv run python -m jeopardy.cli
```
