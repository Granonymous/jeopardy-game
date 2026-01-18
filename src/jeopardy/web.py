import streamlit as st
from pathlib import Path
import random
import gzip
import shutil

from jeopardy.database import get_usable_categories, get_random_clue, create_database, load_clues_to_db, get_final_jeopardy_clue
from jeopardy.data import load_tsv_data, clean_clues
from jeopardy.game import STANDARD_VALUES, DOUBLE_JEOPARDY_VALUES, check_answer, generate_board
from jeopardy.state import create_new_game

DB_PATH = Path("jeopardy.db")
DB_GZ_PATH = Path("jeopardy.db.gz")


def init_database():
    """Initialize database if it doesn't exist."""
    if not DB_PATH.exists():
        # First, try to decompress from .gz file (for cloud deployment)
        if DB_GZ_PATH.exists():
            st.info("Decompressing database for first run...")
            with gzip.open(DB_GZ_PATH, 'rb') as f_in:
                with open(DB_PATH, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            st.rerun()
        else:
            # Fall back to building from TSV (for local development)
            st.info("Setting up database for first run... this may take a moment.")
            create_database(DB_PATH)
            clues = clean_clues(load_tsv_data())
            load_clues_to_db(clues, DB_PATH)
            st.rerun()


def init_round(round_num: int):
    """Initialize a new round (1 = Jeopardy, 2 = Double Jeopardy)."""
    if round_num == 1:
        values = STANDARD_VALUES
        num_daily_doubles = 1
    else:
        values = DOUBLE_JEOPARDY_VALUES
        num_daily_doubles = 2

    categories = random.sample(get_usable_categories(db_path=DB_PATH, round_num=round_num), 6)

    def get_clue(cat, val):
        return get_random_clue(cat, val, DB_PATH, round_num=round_num)

    board = generate_board(categories, get_clue, values)

    # Randomly select Daily Double positions
    all_positions = [(cat, val) for cat in categories for val in values]
    daily_doubles = set(random.sample(all_positions, num_daily_doubles))

    return categories, board, values, daily_doubles


def main():
    st.title("Jeopardy!")


    # Sidebar with reset option
    with st.sidebar:
        st.write("Game Controls")
        if st.button("New Game"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        # Debug info
        st.write("---")
        st.write(f"Round: {st.session_state.get('round_num', 'N/A')}")
        st.write(f"Values: {st.session_state.get('values', 'N/A')}")

    # Initialize database
    init_database()

    # Initialize game state (check for values to handle old sessions)
    if "round_num" not in st.session_state or "values" not in st.session_state:
        st.session_state.round_num = 1
        st.session_state.score = 0
        st.session_state.answered = set()
        categories, board, values, daily_doubles = init_round(1)
        st.session_state.categories = categories
        st.session_state.board = board
        st.session_state.values = values
        st.session_state.daily_doubles = daily_doubles

    round_num = st.session_state.round_num
    score = st.session_state.score
    answered = st.session_state.answered
    categories = st.session_state.categories
    board = st.session_state.board
    values = st.session_state.get("values", STANDARD_VALUES)
    daily_doubles = st.session_state.get("daily_doubles", set())

    # Check if current round is complete
    total_clues = 6 * 5  # 6 categories x 5 values
    if len(answered) >= total_clues:
        if round_num == 1:
            # Transition to Double Jeopardy
            st.success("Round 1 Complete! Moving to Double Jeopardy!")
            if st.button("Start Double Jeopardy"):
                st.session_state.round_num = 2
                st.session_state.answered = set()
                categories, board, values, daily_doubles = init_round(2)
                st.session_state.categories = categories
                st.session_state.board = board
                st.session_state.values = values
                st.session_state.daily_doubles = daily_doubles
                st.rerun()
            return
        elif round_num == 2:
            # Check if eligible for Final Jeopardy
            if score <= 0:
                st.error("You need a positive score to play Final Jeopardy!")
                st.header("Game Over!")
                st.subheader(f"Final Score: ${score:,}")
                if st.button("Play Again"):
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.rerun()
                return
            else:
                st.success("Double Jeopardy Complete! Time for Final Jeopardy!")
                if st.button("Start Final Jeopardy"):
                    st.session_state.round_num = 3
                    st.session_state.fj_clue = get_final_jeopardy_clue(DB_PATH)
                    st.session_state.fj_stage = "wager"
                    st.rerun()
                return

    # Handle Final Jeopardy
    if round_num == 3:
        fj_clue = st.session_state.fj_clue
        fj_stage = st.session_state.get("fj_stage", "wager")

        st.header("Final Jeopardy!")
        st.subheader(f"Current Score: ${score:,}")
        st.markdown(f"### Category: {fj_clue['category']}")

        if fj_stage == "wager":
            st.write(f"How much would you like to wager? (You can wager $0 to ${score:,})")
            wager_input = st.text_input("Wager amount:", value="0", key="fj_wager_input")

            # Validate wager
            try:
                wager = int(wager_input.replace(",", "").replace("$", ""))
                if wager < 0:
                    st.error("Wager must be at least $0")
                    wager = None
                elif wager > score:
                    st.error(f"You can't wager more than your score (${score:,})")
                    wager = None
            except ValueError:
                st.error("Please enter a valid number")
                wager = None

            if st.button("Lock in Wager") and wager is not None:
                st.session_state.fj_wager = wager
                st.session_state.fj_stage = "answer"
                st.rerun()

        elif fj_stage == "answer":
            wager = st.session_state.fj_wager
            st.write(f"Your wager: ${wager:,}")
            st.markdown("---")
            st.write(f'"{fj_clue["question"]}"')
            st.markdown("---")

            answer = st.text_input("Your answer:", key="fj_answer_input")
            if st.button("Submit Final Answer"):
                correct = check_answer(answer, fj_clue["answer"])
                if correct:
                    st.session_state.score += wager
                else:
                    st.session_state.score -= wager
                # Store result to show on done screen
                st.session_state.fj_result = {
                    "correct": correct,
                    "answer": fj_clue["answer"],
                    "wager": wager
                }
                st.session_state.fj_stage = "done"
                st.rerun()

        elif fj_stage == "done":
            # Show Final Jeopardy result
            result = st.session_state.get("fj_result", {})
            if result.get("correct"):
                st.balloons()
                st.success(f"Correct! +${result['wager']:,}")
            else:
                st.error(f"Sorry, that's incorrect. -${result['wager']:,}")
            st.info(f"The correct answer was: {result.get('answer', 'N/A')}")

            st.markdown("---")
            st.header("Game Over!")
            st.subheader(f"Final Score: ${st.session_state.score:,}")
            if st.button("Play Again"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        return

    # Display round and score
    round_name = "Jeopardy!" if round_num == 1 else "Double Jeopardy!"
    st.header(f"{round_name} - Score: ${score:,}")
    st.caption(f"Clues remaining: {total_clues - len(answered)}")

    # Show last result if there is one
    if "last_result" in st.session_state:
        result = st.session_state.last_result
        dd_prefix = "🎯 Daily Double! " if result.get("is_daily_double") else ""
        if result["correct"] is True:
            st.success(f"{dd_prefix}Correct! +${result['value']:,}")
        elif result["correct"] is False:
            st.error(f"{dd_prefix}Sorry! The answer was: {result['answer']}  (-${result['value']:,})")
        else:  # Skipped
            st.info(f"{dd_prefix}Skipped. The answer was: {result['answer']}")
        del st.session_state.last_result

    # Display board as buttons
    cols = st.columns(6)
    for i, cat in enumerate(categories):
        with cols[i]:
            st.write(f"**{cat}**")
            for value in values:
                if (cat, value) not in answered:
                    if st.button(f"${value}", key=f"{cat}-{value}"):
                        st.session_state.selected = (cat, value)
                else:
                    st.write("-")

    # Handle clue selection
    if "selected" in st.session_state:
        cat, val = st.session_state.selected
        clue = board[cat][val]["clue"]
        is_daily_double = (cat, val) in daily_doubles

        # Daily Double wagering
        if is_daily_double and "dd_wager" not in st.session_state:
            st.markdown("### 🎯 DAILY DOUBLE!")
            st.subheader(f"{cat}")

            # Calculate max wager (higher of current score or highest value on board)
            max_board_value = max(values)
            max_wager = max(score, max_board_value) if score > 0 else max_board_value
            min_wager = 5  # Minimum bet is $5

            st.write(f"Your score: ${score:,}")
            st.write(f"You can wager from $5 to ${max_wager:,}")

            wager_input = st.text_input("Your wager:", value=str(min_wager), key=f"dd_wager_{cat}_{val}")

            try:
                wager = int(wager_input.replace(",", "").replace("$", ""))
                if wager < min_wager:
                    st.error(f"Minimum wager is ${min_wager}")
                    wager = None
                elif wager > max_wager:
                    st.error(f"Maximum wager is ${max_wager:,}")
                    wager = None
            except ValueError:
                st.error("Please enter a valid number")
                wager = None

            if st.button("Lock in Wager") and wager is not None:
                st.session_state.dd_wager = wager
                st.rerun()
        else:
            # Regular clue or Daily Double with wager locked in
            wager = st.session_state.get("dd_wager", val)

            if is_daily_double:
                st.markdown("### 🎯 DAILY DOUBLE!")
                st.write(f"Your wager: ${wager:,}")

            st.subheader(f"{cat} for ${val}")
            st.write(f'"{clue["question"]}"')

            answer = st.text_input("Your answer:", key=f"answer_{cat}_{val}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Submit", use_container_width=True):
                    correct = check_answer(answer, clue["answer"])
                    st.session_state.answered.add((cat, val))
                    actual_value = wager if is_daily_double else val
                    if correct:
                        st.session_state.score += actual_value
                    else:
                        st.session_state.score -= actual_value
                    # Store result to display after rerun
                    st.session_state.last_result = {
                        "correct": correct,
                        "answer": clue["answer"],
                        "value": actual_value,
                        "is_daily_double": is_daily_double
                    }
                    del st.session_state.selected
                    if "dd_wager" in st.session_state:
                        del st.session_state.dd_wager
                    st.rerun()
            with col2:
                if st.button("Skip", use_container_width=True):
                    st.session_state.answered.add((cat, val))
                    actual_value = wager if is_daily_double else val
                    # Store result to display after rerun (no penalty)
                    st.session_state.last_result = {
                        "correct": None,  # None indicates skip
                        "answer": clue["answer"],
                        "value": actual_value,
                        "is_daily_double": is_daily_double
                    }
                    del st.session_state.selected
                    if "dd_wager" in st.session_state:
                        del st.session_state.dd_wager
                    st.rerun()


if __name__ == "__main__":
    main()
