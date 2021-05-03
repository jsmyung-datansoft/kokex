#!/usr/bin/env bash

root="$(dirname "$0")/../.."
cd "${root}"

echo "Installing dependencies"
pip3 install --no-cache-dir -r requirements.txt

echo "Starting server"
python3 kokex/server/server.py
