#!/bin/bash
# Launcher script for Rollin' Python Edition

cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python -m venv venv
    echo "Installing dependencies..."
    venv/bin/pip install -r requirements.txt
fi

# Run the game
venv/bin/python src/game.py
