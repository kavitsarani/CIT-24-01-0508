# Personal Expense Tracker

A simple web application to track personal expenses, built with **Python Flask** and **MySQL**, containerized using **Docker** and **Docker Compose**.

## Features

- **Add Expense** – Record an expense with description, category, amount, and date
- **View Expenses** – See all expenses in a clean table view
- **Delete Expense** – Remove individual expenses
- **Calculate Total** – Automatically displays the total of all expenses

## Architecture

```
Browser → Flask Container (expense_web:5000) → Docker Network (expense_network) → MySQL Container (expense_database:3306) → Persistent Volume (expense_data)
```

### Docker Components

| Component | Name | Details |
|-----------|------|---------|
| Web Container | `expense_web` | Flask app on port 5000 |
| Database Container | `expense_database` | MySQL 8.0 on port 3306 |
| Network | `expense_network` | Bridge network |
| Volume | `expense_data` | Persistent MySQL storage |

## Project Structure

```
PersonalExpenseTracker/
├── app/
│   ├── Dockerfile
│   ├── app.py
│   ├── requirements.txt
│   ├── .dockerignore
│   └── templates/
│       └── index.html
├── docker-compose.yaml
├── prepare-app.sh
├── start-app.sh
├── stop-app.sh
├── remove-app.sh
└── README.md
```

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- [VS Code](https://code.visualstudio.com/) (recommended editor)

## Getting Started

### 1. Build the images

```bash
bash prepare-app.sh
```

### 2. Start the application

```bash
bash start-app.sh
```

### 3. Access the application

Open your browser and go to: **http://localhost:5000**

### 4. Stop the application

```bash
bash stop-app.sh
```

### 5. Remove containers and network

```bash
bash remove-app.sh
```

## Database Schema

The MySQL database uses a single table:

```sql
CREATE TABLE expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    description VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    expense_date DATE NOT NULL
);
```

## Docker Configuration Details

- **MySQL Healthcheck**: `mysqladmin ping` ensures MySQL is ready before Flask starts
- **Restart Policy**: `unless-stopped` on both containers for reliability
- **Persistent Volume**: `expense_data` preserves database data across container restarts
- **Docker Networking**: Flask connects to MySQL using the service name `expense_database` (not localhost)
- **Environment Variables**: Database credentials are configured via environment variables in `docker-compose.yaml`

## Shell Scripts

| Script | Purpose |
|--------|---------|
| `prepare-app.sh` | Builds Docker images |
| `start-app.sh` | Starts containers in detached mode |
| `stop-app.sh` | Stops running containers |
| `remove-app.sh` | Removes containers and network (preserves data volume) |

## Technologies Used

- Python Flask 3.0
- MySQL 8.0
- Docker & Docker Compose
- HTML/CSS
