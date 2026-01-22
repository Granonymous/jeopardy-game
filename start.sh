#!/bin/bash
export PYTHONPATH=src
uvicorn jeopardy.multiplayer:app --host 0.0.0.0 --port $PORT
