#!/bin/bash
# prepare-app.sh - Build Docker images for the Personal Expense Tracker

echo "Building Docker images..."
docker-compose build
echo "Build complete!"
