#!/usr/bin/env bash
set -e

sudo apt update
sudo apt install -y python3-venv python3-pip libgpiod2

python3 -m venv .venv
source .venv/bin/activate
pip install --no-cache-dir -r requirements.txt

if [ ! -f x.env ]; then
  cat > x.env <<EOF
USE_MOCK_SENSOR=false
POLL_INTERVAL=10
MONGO_URI=mongodb://localhost:27017
MONGO_DB=your_db_name
MONGO_COLLECTION=your_collection_name
EOF
  echo "Created default x.env; please edit as needed."
fi

echo "Setup complete. Activate with 'source .venv/bin/activate' and run './agent.py' or enable the service."
