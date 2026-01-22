"""
Multiplayer Jeopardy server using FastAPI and WebSockets.

This module handles:
- Room creation and management
- Real-time game state synchronization
- Buzz-in mechanics with timing
- Score tracking for multiple players
"""

import asyncio
import json
import random
import string
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from jeopardy.database import get_usable_categories, get_random_clue, get_final_jeopardy_clue
from jeopardy.game import STANDARD_VALUES, DOUBLE_JEOPARDY_VALUES, check_answer, generate_board

# Find database - check current dir first, then project root
_cwd_db = Path("jeopardy.db")
_project_db = Path(__file__).parent.parent.parent / "jeopardy.db"
DB_PATH = _cwd_db if _cwd_db.exists() else _project_db

# Game timing constants (in seconds)
CLUE_DISPLAY_TIME = 10  # Time to read the clue before buzzing opens
BUZZ_WINDOW_TIME = 10   # Time window to buzz in
ANSWER_TIME = 15        # Time to type answer after buzzing
DD_WAGER_TIME = 10      # Time to place Daily Double wager
FJ_WAGER_TIME = 30      # Time to place Final Jeopardy wager
FJ_ANSWER_TIME = 30     # Time to answer Final Jeopardy


@dataclass
class Player:
    """Represents a player in a multiplayer game."""
    id: str
    name: str
    score: int = 0
    websocket: WebSocket = None

    def to_dict(self):
        return {"id": self.id, "name": self.name, "score": self.score}


@dataclass
class GameRoom:
    """Represents a multiplayer game room."""
    room_id: str
    host_id: str
    players: Dict[str, Player] = field(default_factory=dict)

    # Game state
    round_num: int = 1
    categories: List[str] = field(default_factory=list)
    board: dict = field(default_factory=dict)
    values: List[int] = field(default_factory=list)
    daily_doubles: set = field(default_factory=set)
    answered: set = field(default_factory=set)

    # Current clue state
    current_clue: dict = None
    current_category: str = None
    current_value: int = None

    # Buzzer state
    buzz_open: bool = False
    buzzed_player: str = None
    buzz_time: float = None
    wrong_buzzers: set = field(default_factory=set)  # Players who got it wrong this clue
    buzz_timer_id: int = 0  # Increments each time buzz window opens, used to cancel old timers
    answer_timer_id: int = 0  # Increments each time answer phase starts, used to cancel old timers

    # Board control - who picks the next clue (starts with host, changes when someone answers correctly)
    board_controller: str = None

    # Daily Double state
    dd_wager: int = 0
    dd_player: str = None  # Player who selected the Daily Double

    # Timers
    clue_shown_time: float = None
    answer_deadline: float = None

    # Game phase: "lobby", "selecting", "showing_clue", "buzz_open", "answering", "showing_answer", "round_end", "fj_wagering", "fj_clue", "fj_answering", "fj_reveal", "game_over"
    phase: str = "lobby"

    # Final Jeopardy state
    fj_eligible_players: set = field(default_factory=set)  # Players with positive scores
    fj_wagers: Dict[str, int] = field(default_factory=dict)  # player_id -> wager
    fj_answers: Dict[str, str] = field(default_factory=dict)  # player_id -> answer
    fj_wagers_received: set = field(default_factory=set)  # Players who submitted wagers
    fj_answers_received: set = field(default_factory=set)  # Players who submitted answers

    def to_dict(self):
        return {
            "room_id": self.room_id,
            "host_id": self.host_id,
            "board_controller": self.board_controller,
            "players": {pid: p.to_dict() for pid, p in self.players.items()},
            "round_num": self.round_num,
            "categories": self.categories,
            "values": self.values,
            "answered": list(self.answered),
            "current_clue": self.current_clue,
            "current_category": self.current_category,
            "current_value": self.current_value,
            "buzz_open": self.buzz_open,
            "buzzed_player": self.buzzed_player,
            "phase": self.phase,
        }


# Global room storage
rooms: Dict[str, GameRoom] = {}


def generate_room_id() -> str:
    """Generate a unique 4-character room code."""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase, k=4))
        if code not in rooms:
            return code


def generate_player_id() -> str:
    """Generate a unique player ID."""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))


async def broadcast_to_room(room: GameRoom, message: dict):
    """Send a message to all players in a room."""
    disconnected = []
    for player_id, player in room.players.items():
        if player.websocket:
            try:
                await player.websocket.send_json(message)
            except:
                disconnected.append(player_id)
    # Clean up disconnected players
    for pid in disconnected:
        del room.players[pid]


async def send_to_player(player: Player, message: dict):
    """Send a message to a specific player."""
    if player.websocket:
        try:
            await player.websocket.send_json(message)
        except:
            pass


def init_round(room: GameRoom, round_num: int):
    """Initialize a new round for the room."""
    room.round_num = round_num
    room.answered = set()
    room.current_clue = None
    room.current_category = None
    room.current_value = None
    room.buzz_open = False
    room.buzzed_player = None
    room.wrong_buzzers = set()

    # Board control: host for round 1, lowest score for round 2
    if round_num == 1:
        room.board_controller = room.host_id
    else:
        # Find player with lowest score
        lowest_player = min(room.players.values(), key=lambda p: p.score)
        room.board_controller = lowest_player.id

    if round_num == 1:
        room.values = STANDARD_VALUES
        num_daily_doubles = 1
    elif round_num == 2:
        room.values = DOUBLE_JEOPARDY_VALUES
        num_daily_doubles = 2
    else:
        return  # Final Jeopardy handled separately

    room.categories = random.sample(get_usable_categories(db_path=DB_PATH, round_num=round_num), 6)

    def get_clue(cat, val):
        return get_random_clue(cat, val, DB_PATH, round_num=round_num)

    room.board = generate_board(room.categories, get_clue, room.values)

    # Set daily doubles
    all_positions = [(cat, val) for cat in room.categories for val in room.values]
    room.daily_doubles = set(random.sample(all_positions, num_daily_doubles))

    room.phase = "selecting"


# FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Multiplayer Jeopardy server starting...")
    yield
    # Shutdown
    print("Multiplayer Jeopardy server shutting down...")

app = FastAPI(lifespan=lifespan)


@app.get("/")
async def get_home():
    """Serve the multiplayer game page."""
    return HTMLResponse(content=open(Path(__file__).parent / "multiplayer.html").read())


@app.websocket("/ws/{room_id}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, player_id: str):
    await websocket.accept()

    # Validate room exists
    if room_id not in rooms:
        await websocket.send_json({"type": "error", "message": "Room not found"})
        await websocket.close()
        return

    room = rooms[room_id]

    # Check if this is an existing player reconnecting or new player
    if player_id in room.players:
        player = room.players[player_id]
        player.websocket = websocket
    else:
        await websocket.send_json({"type": "error", "message": "Player not in room"})
        await websocket.close()
        return

    # Send current game state
    await send_to_player(player, {
        "type": "game_state",
        "state": room.to_dict(),
        "your_id": player_id
    })

    # Notify others
    await broadcast_to_room(room, {
        "type": "player_joined",
        "player": player.to_dict()
    })

    try:
        while True:
            data = await websocket.receive_json()
            await handle_message(room, player, data)
    except WebSocketDisconnect:
        # Player disconnected
        await broadcast_to_room(room, {
            "type": "player_left",
            "player_id": player_id,
            "player_name": player.name
        })


@app.post("/create_room")
async def create_room(player_name: str = "Host"):
    """Create a new game room."""
    room_id = generate_room_id()
    player_id = generate_player_id()

    player = Player(id=player_id, name=player_name)
    room = GameRoom(room_id=room_id, host_id=player_id)
    room.players[player_id] = player

    rooms[room_id] = room

    return {"room_id": room_id, "player_id": player_id}


@app.post("/join_room/{room_id}")
async def join_room(room_id: str, player_name: str = "Player"):
    """Join an existing game room."""
    if room_id not in rooms:
        return {"error": "Room not found"}

    room = rooms[room_id]

    if room.phase != "lobby":
        return {"error": "Game already in progress"}

    if len(room.players) >= 4:
        return {"error": "Room is full"}

    player_id = generate_player_id()
    player = Player(id=player_id, name=player_name)
    room.players[player_id] = player

    return {"room_id": room_id, "player_id": player_id}


async def handle_message(room: GameRoom, player: Player, data: dict):
    """Handle incoming WebSocket messages."""
    msg_type = data.get("type")

    if msg_type == "start_game":
        # Only host can start
        if player.id != room.host_id:
            return
        if len(room.players) < 2:
            await send_to_player(player, {"type": "error", "message": "Need at least 2 players"})
            return

        init_round(room, 1)
        await broadcast_to_room(room, {
            "type": "game_started",
            "state": room.to_dict()
        })

    elif msg_type == "select_clue":
        # Only board controller selects clues
        if player.id != room.board_controller:
            return
        if room.phase != "selecting":
            return

        category = data.get("category")
        value = data.get("value")

        if (category, value) in room.answered:
            return

        clue_data = room.board[category][value]["clue"]
        room.current_clue = clue_data
        room.current_category = category
        room.current_value = value
        room.wrong_buzzers = set()
        room.buzzed_player = None
        room.phase = "showing_clue"
        room.clue_shown_time = time.time()

        # Check for daily double
        is_dd = (category, value) in room.daily_doubles

        if not is_dd:
            # Regular clue - show it and start buzz timer
            await broadcast_to_room(room, {
                "type": "clue_selected",
                "category": category,
                "value": value,
                "question": clue_data["question"],
                "is_daily_double": False,
                "clue_display_time": CLUE_DISPLAY_TIME,
                "selector_id": player.id,
                "selector_name": player.name
            })
            asyncio.create_task(open_buzzer_after_delay(room))
        else:
            # Daily Double - show category only and start wagering phase
            room.phase = "dd_wagering"
            room.dd_player = player.id
            room.dd_wager = 0

            # Calculate max wager
            player_obj = room.players[player.id]
            max_board_value = max(room.values)
            max_wager = max(player_obj.score, max_board_value) if player_obj.score > 0 else max_board_value
            min_wager = 5

            await broadcast_to_room(room, {
                "type": "daily_double_wager",
                "category": category,
                "value": value,
                "player_id": player.id,
                "player_name": player.name,
                "player_score": player_obj.score,
                "min_wager": min_wager,
                "max_wager": max_wager,
                "wager_time": DD_WAGER_TIME
            })

    elif msg_type == "submit_dd_wager":
        if room.phase != "dd_wagering":
            return
        if player.id != room.dd_player:
            return

        wager = data.get("wager", 0)
        player_obj = room.players[player.id]
        max_board_value = max(room.values)
        max_wager = max(player_obj.score, max_board_value) if player_obj.score > 0 else max_board_value
        min_wager = 5

        # Validate wager
        if wager < min_wager:
            wager = min_wager
        if wager > max_wager:
            wager = max_wager

        room.dd_wager = wager
        room.phase = "answering"
        room.buzzed_player = player.id
        room.answer_deadline = time.time() + ANSWER_TIME
        room.answer_timer_id += 1
        current_timer_id = room.answer_timer_id

        # Now show the clue
        await broadcast_to_room(room, {
            "type": "daily_double_clue",
            "category": room.current_category,
            "value": room.current_value,
            "question": room.current_clue["question"],
            "wager": wager,
            "player_id": player.id,
            "player_name": player.name,
            "answer_time": ANSWER_TIME
        })

        # Start answer timeout
        asyncio.create_task(dd_answer_timeout(room, current_timer_id))

    elif msg_type == "buzz":
        if room.phase != "buzz_open":
            return
        if player.id in room.wrong_buzzers:
            return  # Already got it wrong

        # First valid buzz wins
        if room.buzzed_player is None:
            room.buzzed_player = player.id
            room.buzz_time = time.time()
            room.phase = "answering"
            room.answer_deadline = time.time() + ANSWER_TIME

            await broadcast_to_room(room, {
                "type": "player_buzzed",
                "player_id": player.id,
                "player_name": player.name,
                "answer_time": ANSWER_TIME
            })

    elif msg_type == "submit_answer":
        if room.phase != "answering":
            return
        if player.id != room.buzzed_player:
            return

        # Cancel any pending answer timeout
        room.answer_timer_id += 1

        answer = data.get("answer", "")
        correct = check_answer(answer, room.current_clue["answer"])

        # Use dd_wager for Daily Doubles, otherwise use clue value
        is_daily_double = room.dd_player is not None
        value = room.dd_wager if is_daily_double else room.current_value

        if correct:
            player.score += value
            room.answered.add((room.current_category, room.current_value))
            # Transfer board control to the player who answered correctly
            room.board_controller = player.id

            await broadcast_to_room(room, {
                "type": "answer_result",
                "correct": True,
                "player_id": player.id,
                "player_name": player.name,
                "answer": answer,
                "correct_answer": room.current_clue["answer"],
                "value": value,
                "is_daily_double": is_daily_double,
                "scores": {pid: p.to_dict() for pid, p in room.players.items()},
                "new_board_controller": player.id
            })

            # Reset DD state
            room.dd_player = None
            room.dd_wager = 0

            # Check if round is over
            await check_round_complete(room)
        else:
            player.score -= value

            # For Daily Double, no one else gets a chance
            if is_daily_double:
                room.answered.add((room.current_category, room.current_value))
                await broadcast_to_room(room, {
                    "type": "answer_result",
                    "correct": False,
                    "player_id": player.id,
                    "player_name": player.name,
                    "answer": answer,
                    "correct_answer": room.current_clue["answer"],
                    "value": value,
                    "is_daily_double": True,
                    "scores": {pid: p.to_dict() for pid, p in room.players.items()},
                    "no_more_buzzers": True
                })
                # Reset DD state
                room.dd_player = None
                room.dd_wager = 0
                await check_round_complete(room)
                return

            room.wrong_buzzers.add(player.id)
            room.buzzed_player = None

            # Check if anyone else can still buzz
            eligible = [pid for pid in room.players if pid not in room.wrong_buzzers]

            if eligible:
                room.phase = "buzz_open"
                room.buzz_timer_id += 1  # New timer ID cancels old timer
                current_timer_id = room.buzz_timer_id
                await broadcast_to_room(room, {
                    "type": "answer_result",
                    "correct": False,
                    "player_id": player.id,
                    "player_name": player.name,
                    "answer": answer,
                    "value": value,
                    "scores": {pid: p.to_dict() for pid, p in room.players.items()},
                    "buzz_reopened": True,
                    "buzz_time": BUZZ_WINDOW_TIME,
                    "wrong_buzzers": list(room.wrong_buzzers)
                })
                asyncio.create_task(close_buzzer_after_delay(room, BUZZ_WINDOW_TIME, current_timer_id))
            else:
                # Everyone got it wrong, show answer
                room.answered.add((room.current_category, room.current_value))
                await broadcast_to_room(room, {
                    "type": "answer_result",
                    "correct": False,
                    "player_id": player.id,
                    "player_name": player.name,
                    "answer": answer,
                    "correct_answer": room.current_clue["answer"],
                    "value": value,
                    "scores": {pid: p.to_dict() for pid, p in room.players.items()},
                    "no_more_buzzers": True
                })
                await check_round_complete(room)

    elif msg_type == "next_clue":
        # Only board controller can advance
        if player.id != room.board_controller:
            return

        room.phase = "selecting"
        room.current_clue = None
        room.current_category = None
        room.current_value = None
        room.buzzed_player = None
        room.wrong_buzzers = set()

        await broadcast_to_room(room, {
            "type": "ready_for_selection",
            "state": room.to_dict()
        })

    elif msg_type == "start_next_round":
        # Only host can start next round
        if player.id != room.host_id:
            return
        if room.phase != "round_end":
            return

        init_round(room, 2)
        await broadcast_to_room(room, {
            "type": "round_started",
            "round_num": 2,
            "state": room.to_dict()
        })

    elif msg_type == "submit_fj_wager":
        if room.phase != "fj_wagering":
            return
        if player.id not in room.fj_eligible_players:
            return
        if player.id in room.fj_wagers_received:
            return  # Already submitted

        wager = data.get("wager", 0)
        max_wager = player.score
        min_wager = 0

        # Clamp wager to valid range
        wager = max(min_wager, min(wager, max_wager))

        room.fj_wagers[player.id] = wager
        room.fj_wagers_received.add(player.id)

        # Notify others that this player submitted
        await broadcast_to_room(room, {
            "type": "fj_wager_submitted",
            "player_id": player.id,
            "player_name": player.name,
            "wagers_received": len(room.fj_wagers_received),
            "wagers_needed": len(room.fj_eligible_players)
        })

        # Check if all wagers are in
        if room.fj_wagers_received == room.fj_eligible_players:
            await start_fj_clue_phase(room)

    elif msg_type == "submit_fj_answer":
        if room.phase != "fj_answering":
            return
        if player.id not in room.fj_eligible_players:
            return
        if player.id in room.fj_answers_received:
            return  # Already submitted

        answer = data.get("answer", "")
        room.fj_answers[player.id] = answer
        room.fj_answers_received.add(player.id)

        # Notify others that this player submitted
        await broadcast_to_room(room, {
            "type": "fj_answer_submitted",
            "player_id": player.id,
            "player_name": player.name,
            "answers_received": len(room.fj_answers_received),
            "answers_needed": len(room.fj_eligible_players)
        })

        # Check if all answers are in
        if room.fj_answers_received == room.fj_eligible_players:
            await reveal_fj_answers(room)


async def open_buzzer_after_delay(room: GameRoom):
    """Open the buzzer after clue display time."""
    await asyncio.sleep(CLUE_DISPLAY_TIME)

    if room.phase == "showing_clue":
        room.phase = "buzz_open"
        room.buzz_open = True
        room.buzz_timer_id += 1  # New timer ID
        current_timer_id = room.buzz_timer_id

        await broadcast_to_room(room, {
            "type": "buzz_open",
            "buzz_time": BUZZ_WINDOW_TIME
        })

        # Start timer to close buzzer if no one buzzes
        asyncio.create_task(close_buzzer_after_delay(room, BUZZ_WINDOW_TIME, current_timer_id))


async def close_buzzer_after_delay(room: GameRoom, delay: float, timer_id: int):
    """Close the buzzer after timeout."""
    await asyncio.sleep(delay)

    # Only close if this timer is still the active one
    if room.buzz_timer_id != timer_id:
        return  # A newer timer has been started, ignore this one

    if room.phase == "buzz_open" and room.buzzed_player is None:
        room.phase = "showing_answer"
        room.buzz_open = False
        room.answered.add((room.current_category, room.current_value))

        await broadcast_to_room(room, {
            "type": "buzz_timeout",
            "correct_answer": room.current_clue["answer"]
        })

        await check_round_complete(room)


async def dd_answer_timeout(room: GameRoom, timer_id: int):
    """Handle timeout for Daily Double answer."""
    await asyncio.sleep(ANSWER_TIME)

    # Only process if this timer is still the active one
    if room.answer_timer_id != timer_id:
        return  # A newer timer has been started, ignore this one

    if room.phase != "answering":
        return  # Already answered

    if room.dd_player is None:
        return  # Not a Daily Double

    # Time's up - mark as wrong
    player = room.players[room.dd_player]
    player.score -= room.dd_wager
    room.answered.add((room.current_category, room.current_value))

    await broadcast_to_room(room, {
        "type": "answer_result",
        "correct": False,
        "player_id": room.dd_player,
        "player_name": player.name,
        "answer": "(no answer - time expired)",
        "correct_answer": room.current_clue["answer"],
        "value": room.dd_wager,
        "is_daily_double": True,
        "scores": {pid: p.to_dict() for pid, p in room.players.items()},
        "no_more_buzzers": True,
        "timeout": True
    })

    # Reset DD state
    room.dd_player = None
    room.dd_wager = 0
    room.buzzed_player = None

    await check_round_complete(room)


async def check_round_complete(room: GameRoom):
    """Check if the current round is complete."""
    total_clues = 6 * 5

    if len(room.answered) >= total_clues:
        if room.round_num == 1:
            room.phase = "round_end"
            await broadcast_to_room(room, {
                "type": "round_complete",
                "round": 1,
                "next_round": 2,
                "scores": {pid: p.to_dict() for pid, p in room.players.items()}
            })
        elif room.round_num == 2:
            # Start Final Jeopardy
            await start_final_jeopardy(room)
    else:
        room.phase = "selecting"


async def start_final_jeopardy(room: GameRoom):
    """Initialize and start Final Jeopardy."""
    room.round_num = 3
    room.current_clue = get_final_jeopardy_clue(DB_PATH)

    # Find eligible players (positive scores)
    room.fj_eligible_players = {pid for pid, p in room.players.items() if p.score > 0}
    room.fj_wagers = {}
    room.fj_answers = {}
    room.fj_wagers_received = set()
    room.fj_answers_received = set()

    if not room.fj_eligible_players:
        # No one has positive score - game over
        room.phase = "game_over"
        await broadcast_to_room(room, {
            "type": "game_over",
            "reason": "No players have positive scores for Final Jeopardy",
            "scores": {pid: p.to_dict() for pid, p in room.players.items()}
        })
        return

    room.phase = "fj_wagering"

    # Send category to eligible players for wagering
    await broadcast_to_room(room, {
        "type": "fj_start_wager",
        "category": room.current_clue["category"],
        "eligible_players": list(room.fj_eligible_players),
        "scores": {pid: p.to_dict() for pid, p in room.players.items()},
        "wager_time": FJ_WAGER_TIME
    })

    # Start wager timeout
    asyncio.create_task(fj_wager_timeout(room))


async def fj_wager_timeout(room: GameRoom):
    """Handle timeout for Final Jeopardy wagering."""
    await asyncio.sleep(FJ_WAGER_TIME)

    if room.phase != "fj_wagering":
        return  # Already moved on

    # Auto-submit $0 wager for anyone who didn't submit
    for pid in room.fj_eligible_players:
        if pid not in room.fj_wagers_received:
            room.fj_wagers[pid] = 0
            room.fj_wagers_received.add(pid)

    await start_fj_clue_phase(room)


async def start_fj_clue_phase(room: GameRoom):
    """Show the Final Jeopardy clue and start answer timer."""
    room.phase = "fj_answering"

    await broadcast_to_room(room, {
        "type": "fj_show_clue",
        "category": room.current_clue["category"],
        "question": room.current_clue["question"],
        "eligible_players": list(room.fj_eligible_players),
        "answer_time": FJ_ANSWER_TIME
    })

    # Start answer timeout
    asyncio.create_task(fj_answer_timeout(room))


async def fj_answer_timeout(room: GameRoom):
    """Handle timeout for Final Jeopardy answering."""
    await asyncio.sleep(FJ_ANSWER_TIME)

    if room.phase != "fj_answering":
        return  # Already moved on

    # Auto-submit empty answer for anyone who didn't submit
    for pid in room.fj_eligible_players:
        if pid not in room.fj_answers_received:
            room.fj_answers[pid] = ""
            room.fj_answers_received.add(pid)

    await reveal_fj_answers(room)


async def reveal_fj_answers(room: GameRoom):
    """Reveal all Final Jeopardy answers and calculate final scores."""
    room.phase = "fj_reveal"

    results = []
    correct_answer = room.current_clue["answer"]

    # Score each player's answer
    for pid in room.fj_eligible_players:
        player = room.players[pid]
        answer = room.fj_answers.get(pid, "")
        wager = room.fj_wagers.get(pid, 0)
        is_correct = check_answer(answer, correct_answer)

        if is_correct:
            player.score += wager
        else:
            player.score -= wager

        results.append({
            "player_id": pid,
            "player_name": player.name,
            "answer": answer,
            "wager": wager,
            "correct": is_correct,
            "new_score": player.score
        })

    # Determine winner
    winner = max(room.players.values(), key=lambda p: p.score)

    room.phase = "game_over"

    await broadcast_to_room(room, {
        "type": "fj_results",
        "correct_answer": correct_answer,
        "results": results,
        "winner_id": winner.id,
        "winner_name": winner.name,
        "final_scores": {pid: p.to_dict() for pid, p in room.players.items()}
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
