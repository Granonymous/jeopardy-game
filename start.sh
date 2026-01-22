#!/bin/bash
set -e

echo "Current directory: $(pwd)"
echo "Files in current directory:"
ls -la

# Decompress database if needed
if [ ! -f jeopardy.db ] && [ -f jeopardy.db.gz ]; then
    echo "Decompressing database..."
    gunzip -k jeopardy.db.gz
    echo "Database ready: $(ls -lh jeopardy.db)"
elif [ -f jeopardy.db ]; then
    echo "Database already exists: $(ls -lh jeopardy.db)"
else
    echo "ERROR: No jeopardy.db or jeopardy.db.gz found!"
fi

# Verify database has tables
echo "Checking database tables..."
sqlite3 jeopardy.db ".tables" || echo "Failed to read database"

export PYTHONPATH=src
uvicorn jeopardy.multiplayer:app --host 0.0.0.0 --port $PORT
