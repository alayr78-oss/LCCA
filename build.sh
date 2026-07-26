#!/bin/bash
# Fail on any error
set -e

echo "Installing frontend dependencies..."
cd frontend
npm install

echo "Building React frontend..."
npm run build
cd ..

echo "Installing backend dependencies..."
pip install -r backend/requirements.txt

echo "Build complete."
