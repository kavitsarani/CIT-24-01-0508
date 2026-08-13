#!/bin/bash
# start-app.sh - Start the Personal Expense Tracker containers

echo "Starting containers..."
docker-compose up -d
echo ""
echo "Containers started! Access the app at: http://localhost:5000"
