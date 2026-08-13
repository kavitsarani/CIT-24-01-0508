#!/bin/bash
# remove-app.sh - Remove containers and network for the Personal Expense Tracker

echo "Removing containers and network..."
docker-compose down
echo "Containers and network removed."
echo "Note: Data volume 'expense_data' is preserved. To remove it, run: docker volume rm expense_data"
