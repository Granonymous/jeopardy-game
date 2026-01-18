# Session Log

This log is maintained by Claude to track learning progress across sessions.

---

## Template

```markdown
## Session N - YYYY-MM-DD

**Duration:** ~X minutes

**Topics covered:**
- Topic 1
- Topic 2

**Exercises/code written:**
- Description of what was built/practiced

**Key wins:**
- What clicked
- What they did well

**Struggles:**
- What was confusing
- Misconceptions that came up

**Concepts to review next time:**
- Concept 1 (why)
- Concept 2 (why)

**Notes for continuity:**
- Where we left off
- What to pick up next session
```

---

## Sessions

## Session 1 - 2026-01-17

**Topics covered:**
- Environment setup (pylearn, PATH)
- Dict access (bracket vs dot notation)
- List of dicts (LODs)
- List comprehensions: transform, filter, combined conditions
- Loaded real Jeopardy sample data

**Exercises/code written:**
- Built clue dicts, extracted fields
- Filtered Jeopardy data by round, value, combined conditions
- Case-insensitive string matching

**Key wins:**
- Already had CS50 foundation - moved fast
- Picked up list comprehension syntax quickly
- Good instinct on variable naming (noticed `data in data` issue)

**Struggles:**
- None significant - prior experience helped

**Concepts to review next time:**
- Type hints (not yet introduced)
- Functions with type annotations

**Notes for continuity:**
- Ready to start Jeopardy project or learn type hints
- Can skip basic fundamentals, go straight to practical patterns

## Session 1 (continued) - 2026-01-17

**Topics covered:**
- Type hints (basic types, collections, Optional/union)
- Phase 1: data.py (all functions)
- Phase 2: database.py (all functions)

**Exercises/code written:**
- load_sample_data, validate_clue, clean_clues, get_categories, filter_by_category
- create_database, load_clues_to_db, get_random_clue, get_usable_categories
- count_clues_by_category, get_category_value_counts, get_total_clue_count

**Key wins:**
- Type hints clicked quickly
- Wrote complex SQL (get_usable_categories with subquery)
- All tests passing for Phase 1 and Phase 2

**Struggles:**
- Indentation issues causing code to run outside `with` blocks
- File corruption from editing (fixed)
- pylearn vs uv run python for imports

**Concepts to review next time:**
- None major - moving fast

**Notes for continuity:**
- Phase 3 (game.py) is next: normalize_answer, check_answer, etc.
- Good momentum, can continue at this pace

## Session 2 - 2026-01-17

**Topics covered:**
- Phase 3: game.py (all functions)
- String processing: removeprefix, replace, lower, strip
- Pure functions concept
- Early return patterns
- Dict key checking with `in`

**Exercises/code written:**
- normalize_answer (prefixes, punctuation removal)
- check_answer (normalize + compare)
- calculate_score_change (simple conditional)
- generate_board (nested dict construction)
- is_board_complete, get_remaining_clues, mark_clue_answered, get_clue_from_board, count_remaining

**Key wins:**
- Caught the "the" → "theory" bug before tests
- Good instinct on code reuse (count_remaining calls get_remaining_clues)
- Understood early return pattern for is_board_complete

**Struggles:**
- Boolean logic with `or` - wrote `if category or value not in board`
- Forgot to save file before running tests (None returns)
- Confused checking vs setting in mark_clue_answered

**Concepts to review next time:**
- None major

**Notes for continuity:**
- Phase 4 (state.py) is next: GameState dataclass, save/load game
- Will introduce dataclasses

---
