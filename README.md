# 🐍 FastAPI IoT Backend Challenge — Milestone 1

This project implements a CRUD API for IoT units using FastAPI, PostgreSQL with the Repository Pattern using `asyncpg`, and Docker for containerization. For more information, please read [this](python-backedn-v2-m1.MD).

## 📦 Setup and Running

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for running tests directly)

### 1. Build and Run the Stack

1.  **Create the `.env` file:** Copy the contents from the provided `.env.example` (or use the values from step 9 above) into a new file named `.env` in the project root.

| Name        | Description                  | Type   | Options | Default   |
| ----------- | ---------------------------- | ------ | ------- | --------- |
| DB_USER     | postgresql db username       | String |         | None      |
| DB_PASSWORD | postgresql db password       | String |         | None      |
| DB_HOST     | postgresql db server address | String |         | 127.0.0.1 |
| DB_PORT     | postgresql db server port    | String |         | 5437      |
| DB_NAME     | postgresql database name     | String |         | None      |

2.  **Start the services:**
    ```bash
    docker-compose up --build -d
    ```
    This command builds the FastAPI image, starts the PostgreSQL container (`db`), and initializes the database with sample data via `init-data.sql`.

### 2. Access the API

The FastAPI service will be running on `http://localhost:8000`.

- **Swagger UI Documentation:** `http://localhost:8000/docs`
- **ReDoc Documentation:** `http://localhost:8000/redoc`

### 3. Running Unit Tests

To run the unit tests inside the container environment:

```bash
docker-compose run api pytest
```
