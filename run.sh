#!/bin/bash

echo "Starting MyVoiceChat API..."
echo "Activating virtual environment..."

if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Running migrations..."
alembic upgrade head

echo "Starting the server..."
uvicorn main:app --reload --host=0.0.0.0 --port=8080
