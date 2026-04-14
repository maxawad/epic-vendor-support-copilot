#!/bin/bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

if [ ! -d venv ]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

echo "Starting Epic Vendor Services FAQ Support Copilot..."
echo "Local:  http://localhost:8000"
echo "Public: https://support-epic.maxawad.com"

uvicorn app.main:app --host 0.0.0.0 --port 8000
