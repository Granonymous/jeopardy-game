# Jeopardy! Game Project

Build a playable Jeopardy game using real clues from the show.

## Why This Project?

This project applies everything from the fundamentals modules in a real context:
- **File I/O** for loading clue data
- **Dictionaries** for game state and board structure
- **Functions** for modular game logic
- **SQL** for querying 200K+ clues efficiently
- **Classes** for organizing state
- **Control flow** for game loops and validation

Plus new concepts you'll learn as you go:
- State management
- User input handling
- Game loops
- Answer normalization

---

## Project Structure

```
src/jeopardy/
├── __init__.py      # Package marker
├── data.py          # Phase 1: Load and clean clue data
├── database.py      # Phase 2: SQLite storage and queries
├── game.py          # Phase 3: Core game logic (pure functions)
├── state.py         # Phase 4: Game state management
└── cli.py           # Phase 5: Terminal interface
```

Each module corresponds to a project phase. Work through them in order!

---

## Phase 1: Data Exploration & Ingestion

**Goal:** Load and understand the Jeopardy data

**Files to implement:** `src/jeopardy/data.py`

**Functions (in order):**
1. `load_sample_data()` - Load the 70-question sample
2. `validate_clue()` - Check if a clue is usable
3. `clean_clues()` - Filter to valid clues only
4. `get_categories()` - Extract unique categories

**Fundamentals used:**
- JSON handling (notebook 06, cells 10-12)
- Dictionaries (notebook 03)
- List comprehensions (notebook 04)
- Context managers (notebook 06, cells 1-6)

**Exploration questions:**
1. How many total clues are in the sample?
2. What categories exist?
3. What values appear? Are they always 200/400/600/800/1000?
4. What does a "bad" clue look like?

**Milestone:** Can run `filter_by_category(clues, 'SCIENCE')` and get results

**Common pitfalls:**
- Forgetting `with` for file handles
- Not handling missing dictionary keys (use `.get()`)

---

## Phase 2: Database Setup

**Goal:** Store clues in SQLite for fast querying

**Files to implement:** `src/jeopardy/database.py`

**Functions (in order):**
1. `create_database()` - Create the clues table
2. `load_clues_to_db()` - Bulk insert clues
3. `get_random_clue()` - Fetch a clue by category/value
4. `get_usable_categories()` - Find complete categories (hardest!)

**Fundamentals used:**
- SQL basics (notebook 11)
- sqlite3 module (notebook 11, cells 3-4)
- Context managers (notebook 06)

**SQL to practice:**
```sql
-- Count clues per category
SELECT category, COUNT(*) FROM clues GROUP BY category;

-- Random clue from SCIENCE at $400
SELECT * FROM clues
WHERE category = 'SCIENCE' AND value = 400
ORDER BY RANDOM() LIMIT 1;
```

**Milestone:** Can execute a query and get a real clue back

**Common pitfalls:**
- Forgetting `conn.commit()` after INSERT
- SQL injection via f-strings (use `?` placeholders!)
- Not closing connections

---

## Phase 3: Game Logic

**Goal:** Build game mechanics as pure functions

**Files to implement:** `src/jeopardy/game.py`

**Functions (in order):**
1. `normalize_answer()` - Strip "what is", punctuation, etc.
2. `check_answer()` - Compare player answer to correct
3. `calculate_score_change()` - Compute score delta
4. `generate_board()` - Create a full game board

**Fundamentals used:**
- Functions (notebook 05)
- String methods (notebook 02)
- Type hints (notebook 05, cell 16)

**Test in pylearn:**
```python
from jeopardy.game import normalize_answer
normalize_answer("What is Mars?")  # Should give "mars"
normalize_answer("The Civil War")  # Should give "civil war"
```

**Milestone:** All functions work when tested in pylearn

**Key concept - Pure Functions:**
These functions have NO side effects. They just take input and return output.
This makes them easy to test and reason about.

**Common pitfalls:**
- Mutable default arguments (notebook 05, cell 13-14!)
- Inconsistent normalization

---

## Phase 4: State Management

**Goal:** Track game progress with a dataclass

**Files to implement:** `src/jeopardy/state.py`

**Functions (in order):**
1. `GameState` class - Define the state structure
2. `select_clue()` - Set current clue
3. `answer_clue()` - Record result and update score
4. `save_game()` / `load_game()` - Persistence

**Fundamentals used:**
- Dataclasses (notebook 10)
- JSON serialization (notebook 06)

**Why separate state from logic?**
- Game logic stays pure (easy to test)
- State changes are explicit
- Can save/load games

**Common pitfalls:**
- Sets aren't JSON serializable (convert to lists)
- Mutable defaults in dataclass fields

---

## Phase 5: Command-Line Interface

**Goal:** Make it playable!

**Files to implement:** `src/jeopardy/cli.py`

**Functions (in order):**
1. `display_board()` - Print the game board
2. `get_category_selection()` - Get category choice
3. `get_value_selection()` - Get value choice
4. `get_player_answer()` - Get answer input
5. `play_game()` - Main game loop!

**Fundamentals used:**
- Control flow (notebook 04)
- String formatting (notebook 02)
- While loops (notebook 04)

**The Game Loop Pattern:**
```python
while not game_over:
    display_current_state()
    action = get_player_action()
    if action is quit:
        break
    process_action(action)
    update_state()
    game_over = check_end_condition()
show_results()
```

**Milestone:** Can play a complete game from start to finish!

**Common pitfalls:**
- Infinite loops (always have exit conditions!)
- Not validating user input

---

## Concept Reference

| Project Code | Fundamental |
|--------------|-------------|
| Loading JSON | Notebook 06 |
| Dictionaries | Notebook 03 |
| List comprehensions | Notebook 04 |
| SQL queries | Notebook 11 |
| String methods | Notebook 02 |
| Functions | Notebook 05 |
| Dataclasses | Notebook 10 |
| While loops | Notebook 04 |
| Testing | Notebook 08 |

---

## Getting Started

**Important:** All functions are STUBS - they just have `pass` and return `None`.
YOU implement them! Tests will fail until you write the code. That's the point.

1. **Verify imports work:**
   ```bash
   uv run python -c "from jeopardy import data; print('OK')"
   ```

2. **Explore the sample data in pylearn:**
   ```python
   import json
   from pathlib import Path

   path = Path('notebooks/data/sample_jeopardy.json')
   with open(path) as f:
       clues = json.load(f)

   print(f"Total clues: {len(clues)}")
   print(f"First clue: {clues[0]}")
   ```

3. **Start implementing `load_sample_data()`**

4. **Test as you go!** Use pylearn to verify each function works.

---

## Running Tests

Tests are your specification! They show exactly what each function should do.
**They will FAIL until you implement the functions** - that's expected and good.

```bash
# Run all jeopardy tests (expect failures until you implement!)
uv run pytest tests/jeopardy/

# Run specific test file
uv run pytest tests/jeopardy/test_game.py

# Run with verbose output
uv run pytest tests/jeopardy/ -v

# Run just one test (useful when implementing)
uv run pytest tests/jeopardy/test_data.py::TestLoadSampleData::test_returns_list -v
```

**Workflow:** Implement a function → run its test → fix until it passes → repeat

---

## Phase 5+: Polish & Extensions

Once the basic game works, consider:

- [ ] Better answer matching (fuzzy matching with `rapidfuzz`)
- [ ] Game statistics (track correct/incorrect across sessions)
- [ ] Category themes (pick related categories)
- [ ] Timer for answers
- [ ] Save/load game progress
- [ ] Multiple players

**Stretch: Streamlit Web UI**

Turn the CLI into a web app! Streamlit makes this surprisingly easy:
```python
import streamlit as st
# Your game logic stays the same, just different display!
```

---

## Tips for Success

1. **Work incrementally** - One function at a time
2. **Test in pylearn first** - Before writing test files
3. **Read the docstrings** - They have hints!
4. **Connect to fundamentals** - "This is like what we did in notebook X"
5. **Ask for hints** - Use `/hint` when stuck
6. **Celebrate wins** - Playing your first game is a big deal!
