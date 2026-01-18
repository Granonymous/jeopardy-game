# Python Learning Curriculum

## Overview

This curriculum has two phases:
1. **Fundamentals** (~2-3 weeks) - Core Python concepts, enough to read and write basic programs
2. **Project** (~3-4 weeks) - Jeopardy data analysis project, applying concepts in context

The fundamentals phase is more structured. The project phase is more exploratory, with concepts introduced as needed.

---

## Phase 1: Fundamentals

### Module 1: Environment & Tooling
**Goal:** Get set up with modern Python development environment

- [ ] Terminal/CLI basics (cd, ls, pwd, etc.)
- [ ] Installing uv
- [ ] Creating a project with `uv init`
- [ ] Understanding virtual environments (what they are, why they exist)
- [ ] Installing packages with `uv add`
- [ ] Running Python files and the REPL
- [ ] VS Code setup (or preferred editor)

**Exercise:** Create a new project, add a package (like `rich`), write a hello world that uses it.

---

### Module 2: Data Types & Variables
**Goal:** Understand Python's core data types and how they behave

- [ ] Integers, floats, strings, booleans
- [ ] Type checking with `type()`
- [ ] Variables and assignment
- [ ] String operations (slicing, methods, f-strings)
- [ ] Type conversion
- [ ] `None` and its uses
- [ ] Introduction to type hints

**Key concepts to verify:**
- Difference between `=` and `==`
- String immutability
- What happens with integer division (`//` vs `/`)

**Exercise:** Write a program that takes a name and birth year, calculates age, and prints a formatted greeting.

---

### Module 3: Collections
**Goal:** Understand Python's built-in collection types and when to use each

- [ ] Lists - creation, indexing, slicing, methods
- [ ] Tuples - immutability, unpacking
- [ ] Dictionaries - key-value pairs, access patterns, methods
- [ ] Sets - uniqueness, set operations
- [ ] When to use which (decision framework)
- [ ] Mutability vs immutability
- [ ] Nested structures

**Key concepts to verify:**
- Can explain why you'd use a dict vs a list
- Understands what "mutable" means and its implications
- Can access nested data confidently

**Exercise:** Model some real data (maybe a simple version of Jeopardy questions) using appropriate collection types. Justify the choices.

---

### Module 4: Control Flow
**Goal:** Write programs that make decisions and repeat actions

- [ ] `if`/`elif`/`else`
- [ ] Comparison operators
- [ ] Boolean logic (`and`, `or`, `not`)
- [ ] `for` loops - iterating over collections
- [ ] `while` loops - condition-based repetition
- [ ] `break` and `continue`
- [ ] List comprehensions (basic)
- [ ] `enumerate()` and `zip()`
- [ ] Nested loops

**Key concepts to verify:**
- Truthy/falsy values
- When to use for vs while
- Can trace through a loop mentally (this is crucial - practice extensively)
- Understands loop variable scope

**Common stumbling blocks to watch for:**
- Off-by-one errors
- Modifying a list while iterating over it
- Confusion about what `range()` actually produces
- Nested loop execution order (which runs "faster"?)

**Loop tracing exercises:**
Have him trace through loops by hand before running:
```python
result = []
for i in range(3):
    for j in range(2):
        result.append((i, j))
# What is result?
```

**Exercise:** Write a program that filters a list of Jeopardy questions by category and difficulty.

---

### Module 4b: Recursion
**Goal:** Understand recursive thinking (conceptually important even if used sparingly)

- [ ] What recursion is (function calling itself)
- [ ] Base case vs recursive case
- [ ] Call stack visualization
- [ ] Simple recursive examples (factorial, fibonacci)
- [ ] When recursion is natural vs when loops are better
- [ ] Tail recursion (conceptually)

**Key concepts to verify:**
- Can identify base case and recursive case
- Understands why base case is necessary (infinite recursion)
- Can trace through recursive calls mentally
- Knows Python has recursion limits (and why)

**Note:** Don't over-emphasize recursion. It's important to understand but Python isn't optimized for it. The goal is mental model, not making everything recursive.

**Common stumbling blocks:**
- Forgetting the base case
- Not reducing toward the base case
- Confusion about return values bubbling back up
- Thinking recursively vs iteratively (different mental models)

**Exercise:** Implement a recursive function to flatten a nested list, then implement the same thing with a loop. Compare.

---

### Module 5: Functions
**Goal:** Write reusable, well-structured code

- [ ] Defining functions with `def`
- [ ] Parameters and arguments
- [ ] Return values
- [ ] Default arguments
- [ ] Type hints for functions
- [ ] Scope (local vs global)
- [ ] Docstrings
- [ ] Pure functions vs side effects

**Key concepts to verify:**
- Difference between `return` and `print`
- Can explain what happens to variables inside a function
- Understands why pure functions are often preferable

**Exercise:** Refactor previous exercises to use functions. Write docstrings.

---

### Module 6: File I/O & Error Handling
**Goal:** Read and write files, handle things going wrong

- [ ] Reading text files
- [ ] Writing text files
- [ ] Context managers (`with` statement)
- [ ] `pathlib` for file paths
- [ ] CSV reading/writing basics
- [ ] JSON reading/writing
- [ ] `try`/`except`/`finally`
- [ ] Common exceptions and what they mean
- [ ] When to catch vs when to let errors propagate

**Key concepts to verify:**
- Why use `with` instead of manual open/close
- Can read a traceback and identify the problem
- Knows not to catch exceptions too broadly

**Exercise:** Read a CSV of Jeopardy data, process it, handle missing/malformed rows gracefully.

---

### Module 7: Modules & Project Structure
**Goal:** Organize code into multiple files, use external libraries

- [ ] Importing modules
- [ ] Creating your own modules
- [ ] `__name__ == "__main__"` pattern
- [ ] Project structure conventions
- [ ] Finding and evaluating packages
- [ ] Reading documentation effectively

**Exercise:** Restructure the Jeopardy code into a proper project with multiple modules.

---

### Module 8: Testing
**Goal:** Write tests to verify code works and catch regressions

- [ ] Why test (motivation)
- [ ] pytest basics
- [ ] Writing simple test functions
- [ ] Assertions
- [ ] Running tests with `uv run pytest`
- [ ] Test organization
- [ ] What to test vs what not to test

**Exercise:** Write tests for the Jeopardy data processing functions.

---

### Module 9: Git & GitHub
**Goal:** Version control basics, collaboration workflow

- [ ] What is version control (conceptually)
- [ ] `git init`, `git add`, `git commit`
- [ ] Writing good commit messages
- [ ] `git status`, `git log`, `git diff`
- [ ] `.gitignore`
- [ ] Creating a GitHub repo
- [ ] `git push`, `git pull`
- [ ] Branches (basic)
- [ ] Pull requests (conceptually)

**Exercise:** Initialize the Jeopardy project as a git repo, push to GitHub.

---

### Module 10: Classes & OOP (Light)
**Goal:** Understand objects enough to use libraries and structure data

- [ ] What is a class (mental model)
- [ ] Defining simple classes
- [ ] `__init__` and instance attributes
- [ ] Methods
- [ ] `@dataclass` decorator (modern approach)
- [ ] When to use classes vs other structures

**Note:** Don't go deep on inheritance, abstract classes, etc. Just enough to understand how libraries work and model simple domain objects.

**Exercise:** Create a `Question` dataclass for Jeopardy questions.

---

### Module 11: SQL Basics
**Goal:** Query and manipulate data in relational databases

- [ ] What is a relational database (mental model)
- [ ] Setting up SQLite (comes with Python!)
- [ ] Basic SQL syntax: SELECT, FROM, WHERE
- [ ] Filtering and sorting: ORDER BY, LIMIT
- [ ] Aggregations: COUNT, SUM, AVG, GROUP BY
- [ ] Joins (INNER, LEFT) - conceptually important
- [ ] Creating tables and INSERT
- [ ] Using SQL from Python (sqlite3 module)
- [ ] When SQL vs pandas/polars makes sense

**Key concepts to verify:**
- Can write a query to filter and aggregate
- Understands what a JOIN does
- Knows when SQL is the right tool

**Exercise:** Load the Jeopardy question data into SQLite, write queries to answer:
- How many questions are in each category?
- What are the 20 most common categories?
- Get 5 random $400 questions from a specific category
- Find categories that have at least 5 questions at each value level ($200-$1000)

**Note:** SQL is everywhere in data work. Even a basic understanding opens many doors.

---

## Phase 2: Jeopardy Game Project

### Project Overview
Build a playable Jeopardy! game in Python using real clues from the show.

**What you'll build:**
- A data pipeline to ingest and clean 500K+ real Jeopardy clues
- A SQLite database to store and query clues
- A playable game with categories, clue selection, scoring
- (Stretch) A simple web interface with streamlit

**Why this project:**
- Covers real CS fundamentals: state management, game loops, user input, data structures
- Uses real data that needs cleaning and validation
- Natural progression from simple CLI to fancier UI
- More fun than replicating an analysis you already did!

### Data Source
Two good options:

**Option A: Hugging Face Dataset (Recommended for learning)**
- 216,930 questions in JSON format
- Clean structure: category, value, question, answer, round, show_number, air_date
- Can load directly: `from datasets import load_dataset; ds = load_dataset("jeopardy-datasets/jeopardy")`
- Or download the JSON and work with it directly (better for learning file I/O)

**Option B: jwolle1/jeopardy_clue_dataset (More comprehensive)**
- 538,845 clues from Season 1-41 (1984-2025)
- TSV format, slightly different structure
- Already cleaned to remove image/video/audio-dependent clues

We'll use **Option A** - it's cleaner for learning JSON handling and has plenty of questions.

**Important Jeopardy terminology:**
- In the data, "question" is actually the clue shown to contestants
- "answer" is the correct response (what contestants say)
- This is backwards from how we'd normally think about it!

### Data Pipeline
```
raw TSV → validation/cleaning → SQLite DB → game queries
```

### Project Modules

#### P1: Data Ingestion & Exploration
- [ ] Download the Jeopardy JSON (or use `datasets` library)
- [ ] Load into a notebook and explore
  - How many questions total?
  - How many per round (Jeopardy!, Double Jeopardy!, Final Jeopardy!)?
  - What's the distribution of values ($200, $400, etc.)?
  - Most common categories?
  - Sample some questions - do they look usable for a game?
- [ ] Identify data quality issues:
  - Questions with images/video references (messy text)
  - Missing values
  - Weird categories
- [ ] Filter to "good" questions for the game

**New concepts:** JSON handling, exploratory data analysis, data cleaning decisions

**Milestone:** Can answer questions like "How many $400 clues are there in the HISTORY category?" and "What are the top 20 categories by question count?"

---

#### P2: Database Setup & SQL Practice
- [ ] Design the database schema
  - What tables do you need? (probably just one for clues)
  - What columns? What types?
  - Any indexes for faster queries?
- [ ] Create SQLite database
- [ ] Write Python script to load JSON into DB
- [ ] Practice SQL queries:
  - Get all clues from a specific category
  - Get 5 random clues at a specific value
  - Count clues by round
  - Find categories with at least 5 clues at each value level (usable for game boards!)
  - Which air_date has the most questions?

**New concepts:** SQLite, database design, SQL from Python, batch inserts

**Milestone:** Can run a query like this and get a real clue:
```sql
SELECT question, answer FROM clues 
WHERE category = 'HISTORY' AND value = 400 
ORDER BY RANDOM() LIMIT 1
```

---

#### P3: Game Logic (No UI Yet)
Build the core game mechanics as pure functions first:

- [ ] **Board generation:**
  - Select 6 categories (maybe from a theme or random)
  - For each category, get clues at $200, $400, $600, $800, $1000
  - Handle categories that don't have all 5 values
  
- [ ] **Game state:**
  - Track which clues have been used
  - Track player score
  - Track current clue (if any)
  
- [ ] **Answer checking:**
  - Normalize answers (lowercase, strip punctuation)
  - Handle "close enough" matching (fuzzy matching?)
  - Jeopardy quirk: the "question" is the answer, "answer" is the clue

- [ ] **Scoring:**
  - Add value for correct, subtract for incorrect
  - Daily doubles? (stretch goal)

**New concepts:** State management, data structures for game state, string processing

**Milestone:** Can call functions like `generate_board()`, `select_clue(category, value)`, `check_answer(response)` and they work correctly

---

#### P4: Command-Line Interface
Make it playable in the terminal:

- [ ] Display the board (ASCII art or simple grid)
- [ ] Let player select category and value
- [ ] Show the clue, get player's response
- [ ] Check answer, update score, show result
- [ ] Loop until board is cleared or player quits
- [ ] End game summary

**New concepts:** User input, game loops, terminal output formatting

**Example interaction:**
```
Score: $1200

        HISTORY    SCIENCE    SPORTS    MOVIES    FOOD    WORDS
$200      -         $200       -        $200      -       $200
$400     $400        -        $400       -       $400      -
$600     $600       $600      $600      $600     $600     $600
$800     $800       $800      $800      $800     $800     $800
$1000    $1000      $1000     $1000     $1000    $1000    $1000

Select category: HISTORY
Select value: 400

Category: HISTORY for $400
"This document, signed in 1215, limited the power of English monarchs"

Your response: what is the magna carta

Correct! +$400
```

**Milestone:** Can play a full game from start to finish in the terminal

---

#### P5: Polish & Extensions
- [ ] Add game modes:
  - Single player practice
  - Timed responses
  - Category selection (pick your categories vs random)
- [ ] Improve answer matching (fuzzy matching, handle common variations)
- [ ] Add Final Jeopardy round
- [ ] Track statistics across games (win rate, favorite categories, etc.)
- [ ] Save/load game progress

**Stretch goals:**
- [ ] **Streamlit web UI** - Make it look like a real Jeopardy board
- [ ] **Multiplayer** - Multiple players taking turns
- [ ] **AI opponent** - Have Claude play against you (API call for each clue)
- [ ] **Category analysis** - Which categories are you best/worst at?

---

### Key CS Concepts Covered

This project naturally teaches:

| Concept | Where it comes up |
|---------|-------------------|
| Data structures | Game state (dicts, lists), board representation |
| Control flow | Game loop, conditionals for answer checking |
| Functions | Modular game logic |
| File I/O | Loading TSV, database operations |
| SQL | Querying clues from database |
| String processing | Answer normalization and matching |
| State management | Tracking score, used clues, current game |
| Error handling | Invalid input, missing data |
| Testing | Test answer matching, board generation |
| User input | CLI interaction |

---

## Concepts to Weave Throughout

These aren't separate modules but should come up repeatedly:

- **Reading error messages** - every time something breaks
- **Debugging strategies** - print debugging, using debugger, rubber duck
- **Code style** - ruff, consistent formatting, meaningful names
- **Documentation** - docstrings, comments, README
- **Asking good questions** - how to search, how to ask for help effectively

---

## Review Triggers

Revisit concepts when:
- 7+ days since last practice
- It comes up naturally in project work
- Previous session showed uncertainty
- Building on top of it (e.g., review functions before doing testing)
