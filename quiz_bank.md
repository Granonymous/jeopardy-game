# Quiz Bank

Use these for spaced repetition checks. Mix them in naturally during sessions.

## Data Types & Variables

### Quick Checks
- What's the difference between `=` and `==`?
- What does `type([1, 2, 3])` return?
- What's the difference between `5 / 2` and `5 // 2`?
- Is a string mutable or immutable?
- What does `None` represent?

### Predict the Output
```python
x = "hello"
x[0] = "H"
print(x)
```
> Answer: TypeError - strings are immutable

```python
a = 10
b = a
a = 20
print(b)
```
> Answer: 10 (integers are immutable, b still points to 10)

```python
name = "alice"
print(f"Hello, {name.upper()}!")
```
> Answer: "Hello, ALICE!"

---

## Collections

### Quick Checks
- When would you use a dict instead of a list?
- What's the difference between a list and a tuple?
- How do you check if a key exists in a dictionary?
- What happens if you try to add a duplicate to a set?
- Can you use a list as a dictionary key? Why or why not?

### Predict the Output
```python
a = [1, 2, 3]
b = a
b.append(4)
print(a)
```
> Answer: [1, 2, 3, 4] (lists are mutable, a and b point to same object)

```python
d = {"a": 1, "b": 2}
print(d.get("c", 0))
```
> Answer: 0 (default value when key doesn't exist)

```python
s = {1, 2, 2, 3, 3, 3}
print(len(s))
```
> Answer: 3 (sets only keep unique values)

```python
items = ["a", "b", "c"]
print(items[-1])
```
> Answer: "c" (negative indexing from end)

---

## Control Flow

### Quick Checks
- What values are "falsy" in Python?
- When would you use `while` instead of `for`?
- What does `break` do? What about `continue`?
- What does `range(5)` actually produce?

### Predict the Output
```python
for i in range(3):
    print(i)
```
> Answer: 0, 1, 2 (on separate lines)

```python
x = []
if x:
    print("truthy")
else:
    print("falsy")
```
> Answer: "falsy" (empty list is falsy)

```python
result = []
for i in range(3):
    for j in range(2):
        result.append((i, j))
print(len(result))
```
> Answer: 6 (3 * 2 combinations)

```python
nums = [1, 2, 3, 4, 5]
evens = [x for x in nums if x % 2 == 0]
print(evens)
```
> Answer: [2, 4]

---

## Recursion

### Quick Checks
- What are the two essential parts of a recursive function?
- What happens if you forget the base case?
- Why does Python have a recursion limit?

### Trace Through
```python
def countdown(n):
    if n <= 0:
        return "done"
    print(n)
    return countdown(n - 1)

countdown(3)
```
> Answer: Prints 3, 2, 1, returns "done"

```python
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

factorial(4)
```
> Answer: 24 (4 * 3 * 2 * 1)
> Trace: factorial(4) → 4 * factorial(3) → 4 * 3 * factorial(2) → 4 * 3 * 2 * factorial(1) → 4 * 3 * 2 * 1 → 24

---

## Functions

### Quick Checks
- What's the difference between `print()` and `return`?
- What happens to variables defined inside a function when the function ends?
- What's a "pure" function?
- What's the purpose of a docstring?

### Predict the Output
```python
def greet(name="World"):
    return f"Hello, {name}!"

print(greet())
```
> Answer: "Hello, World!"

```python
def add_item(item, lst=[]):
    lst.append(item)
    return lst

print(add_item(1))
print(add_item(2))
```
> Answer: [1], then [1, 2] (mutable default argument gotcha!)

```python
x = 10
def change_x():
    x = 20
change_x()
print(x)
```
> Answer: 10 (function created local x, didn't modify global)

---

## File I/O & Errors

### Quick Checks
- Why use `with open(...)` instead of just `open()`?
- What's the difference between read mode and write mode?
- When should you catch an exception vs let it propagate?
- What does `pathlib.Path` give you over string paths?

### Conceptual
- You get a `FileNotFoundError`. What are the first things you check?
- You get a `KeyError`. What does that usually mean?
- What's wrong with `except:` (bare except)?

---

## Testing

### Quick Checks
- Why write tests? (Give at least 2 reasons)
- What makes a good test name?
- What's the difference between a test passing and the code being correct?

---

## Git

### Quick Checks
- What's the difference between `git add` and `git commit`?
- Why write good commit messages?
- What goes in `.gitignore`?
- What's the point of branches?

---

## Classes

### Quick Checks
- What does `__init__` do?
- What's `self`?
- When would you use a dataclass?

### Predict the Output
```python
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int

p = Point(3, 4)
print(p.x + p.y)
```
> Answer: 7

---

## SQL

### Quick Checks
- What does SELECT do? What about WHERE?
- What's the difference between INNER JOIN and LEFT JOIN?
- When would you use GROUP BY?

### Write the Query
- Get all games where the winner scored over $30,000
- Count how many games each season had
- Find the average winning score, grouped by whether it was before or after James Holzhauer

---

## Polars / Data Analysis

### Quick Checks
- What's a DataFrame?
- What's the difference between selecting a column and filtering rows?
- Why might you use lazy evaluation?

### Conceptual
- You have a DataFrame and need to: filter rows, add a new column, then group and aggregate. What's the general pattern?

---

## Game Development Concepts

### Quick Checks
- What is "state" in a game? Give an example from the Jeopardy game.
- Why separate game logic from UI/display code?
- What's a game loop?

### Conceptual
- You're building a game where players take turns. What data do you need to track?
- How would you represent a Jeopardy board in Python? (What data structure?)
- Why is it useful to build game logic as pure functions before adding a UI?

### Predict the Behavior
```python
board = {
    "HISTORY": {200: "clue1", 400: "clue2", 600: None},
    "SCIENCE": {200: "clue3", 400: None, 600: "clue4"}
}

# Player selects HISTORY for 600
clue = board["HISTORY"][600]
if clue is None:
    print("Already answered!")
else:
    print(clue)
    board["HISTORY"][600] = None
```
> What prints? What's the board state after?
> Answer: "Already answered!" - the 600 slot was already None

---

## Meta-Skills

### Debugging
- You get an error. What's your first step?
- How do you read a traceback?
- When is `print()` debugging appropriate vs using a debugger?

### Reading Docs
- You need to use a library function you haven't used before. Walk through how you'd figure out how to use it.

---

## Usage Notes for Tutor

**When to use these:**
- Beginning of session: Quick warm-up on recently learned concepts
- When topic comes up naturally: "Before we use a dict here, quick check - when would you pick a dict over a list?"
- After 7+ days: Review older concepts
- When building on a concept: Make sure foundation is solid

**How to use:**
- Don't rapid-fire quiz - weave in naturally
- "Predict the output" is especially valuable - builds mental execution
- If they get it wrong, don't just give the answer - explore why
- Track which concepts need more review in progress.json

**Difficulty levels:**
- Quick Checks: Should be automatic after the concept is solid
- Predict the Output: Requires active mental execution
- Trace Through: Most demanding, especially for recursion
- Conceptual: Tests understanding, not just recall

---

## Jeopardy Project - Phase-Specific Questions

### Phase 1: Data Loading

#### Quick Checks
- What fields does a Jeopardy clue have?
- What makes a clue "unusable" for a text-based game?
- Why use `with open(...)` when loading JSON?

#### Predict the Output
```python
clue = {"category": "SCIENCE", "value": 400, "question": "Red planet"}
print(clue.get("answer", "No answer"))
```
> Answer: "No answer" (key doesn't exist, returns default)

```python
clues = [{"category": "SCIENCE"}, {"category": "HISTORY"}, {"category": "SCIENCE"}]
categories = set(c["category"] for c in clues)
print(sorted(categories))
```
> Answer: ['HISTORY', 'SCIENCE'] (set removes duplicates, sorted alphabetizes)

---

### Phase 2: Database

#### Quick Checks
- Why use a database instead of keeping all clues in a Python list?
- What's the difference between `execute()` and `executemany()`?
- Why use `?` placeholders instead of f-strings in SQL?

#### Write the Query
Get a random clue from SCIENCE at $400:
> `SELECT * FROM clues WHERE category = 'SCIENCE' AND value = 400 ORDER BY RANDOM() LIMIT 1`

Count clues per category, sorted by count:
> `SELECT category, COUNT(*) as n FROM clues GROUP BY category ORDER BY n DESC`

Find categories with at least 5 clues at the $400 level:
> `SELECT category FROM clues WHERE value = 400 GROUP BY category HAVING COUNT(*) >= 5`

---

### Phase 3: Game Logic

#### Quick Checks
- What are three things you should normalize in a Jeopardy answer?
- Why are the game logic functions "pure"?
- What data structure represents the game board?

#### Predict the Output
```python
def normalize(answer):
    answer = answer.lower().strip()
    if answer.startswith("what is "):
        answer = answer[8:]
    return answer

print(normalize("What is Mars?"))
print(normalize("  MARS  "))
```
> Answer: "mars?" (still has the question mark!), "mars"

```python
def check_answer(player, correct):
    return normalize(player) == normalize(correct)

print(check_answer("What is Mars", "Mars"))
```
> Answer: This would need the normalize function to also handle punctuation.
> The "?" from the original clue and lack of "?" from "What is Mars" would cause mismatch depending on implementation.

#### Think About
- What should happen if `check_answer("Albert Einstein", "Einstein")` is called?
- What are the tradeoffs of being strict vs lenient with answer matching?

---

### Phase 4: CLI & Game Loop

#### Quick Checks
- What are the main steps in a game loop?
- Why is input validation important?
- How do you know when the game is over?

#### Predict the Behavior
```python
score = 0
remaining = 3

while remaining > 0:
    answer = input("Answer: ")  # Assume: "correct", "wrong", "correct"
    if answer == "correct":
        score += 100
    else:
        score -= 100
    remaining -= 1

print(score)
```
> If inputs are "correct", "wrong", "correct": score = 100 (100 - 100 + 100)

#### Design Question
You're implementing `get_category_selection()`. What should happen if the user types:
- A valid number like "1"
- An invalid number like "99"
- Text like "banana"
- "q" or "quit"
- Just presses Enter

---

### Phase 5: State Management

#### Quick Checks
- Why separate state from game logic?
- How do you serialize a set to JSON?
- What's `field(default_factory=set)` for?

#### Predict the Output
```python
from dataclasses import dataclass, field

@dataclass
class GameState:
    score: int = 0
    answered: set = field(default_factory=set)

state = GameState()
state.answered.add(("SCIENCE", 400))
state.score += 400

print(state.score)
print(("SCIENCE", 400) in state.answered)
```
> Answer: 400, True

#### Think About
- What would go wrong if you wrote `answered: set = set()` instead of using `field(default_factory=set)`?
> Answer: All instances would share the same set! The mutable default argument gotcha, but for dataclasses.
