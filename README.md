# Python Learning with Claude Code

This is a structured Python learning environment designed to be used with Claude Code as an AI tutor.

## How It Works

Instead of Claude Code just writing code for you, it operates in **tutor mode**:

- **Socratic approach**: Claude will ask you questions before giving answers, helping you think through problems
- **Predict-before-run**: You'll be asked to predict what code will do before running it
- **Spaced repetition**: Concepts come back up over time to reinforce learning
- **Progress tracking**: Your understanding is tracked so Claude knows what to review

## Getting Started

1. Install [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
2. Clone this repo
3. Run `uv sync` to install dependencies
4. Add the bin directory to your PATH:
   ```bash
   export PATH="$PATH:$(pwd)/bin"
   ```
   (Add this to your `.zshrc` or `.bashrc` to make it permanent)
5. Run `claude` in this directory
6. Run `/start-session` to begin!

## Files

- `CLAUDE.md` - Instructions for Claude on how to tutor (you can read this too!)
- `curriculum.md` - The full learning path with modules and exercises
- `progress.json` - Tracks what you've learned and what needs review

## The Curriculum

### Phase 1: Fundamentals (~2-3 weeks)
Core Python concepts, modern tooling, and good practices:
- Environment setup (uv, virtual environments)
- Data types, collections, control flow
- Recursion and tricky concepts (with extensive tracing practice)
- Functions, file I/O, error handling
- Testing, Git, basic OOP
- SQL basics with SQLite

### Phase 2: Project (~3-4 weeks)
Build a playable Jeopardy! game using 216K+ real questions:
- Data pipeline: JSON → SQLite → game queries
- Game logic: board generation, scoring, answer checking
- CLI interface to play in terminal
- (Stretch) Web UI with streamlit

## Learning Tools

### Slash Commands
- `/start-session` - Begin a learning session, get review questions, see where you left off
- `/end-session` - Wrap up, save progress, log what you learned
- `/progress` - See your progress through the curriculum
- `/quiz` - Quick review questions on past concepts
- `/hint` - Get a hint on the current exercise (without the answer!)
- `/lesson [topic]` - Start an interactive lesson on a topic
- `/show-terminal` - Show Claude what you did in the Python REPL

### pylearn
Instead of running `python3`, run `pylearn` in your terminal. It's a Python REPL that logs your session so Claude can see what you tried:

```bash
$ pylearn
Python 3.11 - Learning REPL
Session logged to: .terminal_log
>>> x = 5
>>> x + 10
15
```

When you come back to Claude and say "I tried it", Claude can run `/show-terminal` to see exactly what happened.

### Jupyter Notebooks
Reference material and structured exercises. Claude will point you to specific cells when relevant.

### Quiz Bank
Spaced repetition questions that come up during `/start-session` and `/quiz`.

## Modern Tooling

This curriculum uses current best practices:
- **uv** instead of pip (faster, better)
- **polars** instead of pandas (faster, cleaner API)
- **ruff** for linting
- **pytest** for testing
- **Type hints** from the start

## Tips

- **Don't rush.** Understanding > completion speed
- **Actually predict** what code will do before running it
- **Ask "why"** - Claude will explain, and the explanation helps
- **It's okay to struggle** - that's where learning happens
- **Take breaks** - spaced practice beats cramming

## When You Get Stuck

1. Read the error message carefully (really read it)
2. Try to identify what went wrong yourself first
3. Ask Claude to help you understand, not just fix it
4. If you're frustrated, take a break - seriously

## Questions?

Ask Claude! It knows about this setup and can explain how things work.
