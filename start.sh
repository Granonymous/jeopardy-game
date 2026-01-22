#!/bin/bash
set -e

# Decompress database if needed
if [ ! -f jeopardy.db ] && [ -f jeopardy.db.gz ]; then
    echo "Decompressing database..."
    gunzip -k jeopardy.db.gz
    echo "Database ready: $(ls -lh jeopardy.db)"
fi

export PYTHONPATH=src
uvicorn jeopardy.multiplayer:app --host 0.0.0.0 --port $PORT
