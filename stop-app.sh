#!/bin/bash
# stop-app.sh - Stop the Personal Expense Tracker containers

echo "Stopping containers..."
docker-compose stop
echo "Containers stopped."
