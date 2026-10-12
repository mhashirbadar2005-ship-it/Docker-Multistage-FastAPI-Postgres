# Docker Multi-Stage Build: FastAPI + PostgreSQL

A small FastAPI application backed by PostgreSQL, packaged with a multi-stage Dockerfile and run with Docker Compose. Built as a DevOps internship task to practice image size optimization, secure environment variable handling, and container port mapping.

## What this project demonstrates

- **Multi-stage Dockerfile**: a builder stage installs dependencies, and a lean runtime stage ships only the installed packages and the app code
- **Smaller image footprint**: build tools (gcc, libpq-dev) and caches stay out of the final image
- **Secure configuration**: database credentials are supplied at runtime from a `.env` file; nothing sensitive is baked into the image
- **Non-root container**: the app runs as an unprivileged `appuser`
- **Port mapping**: the app is published on port 8000, while the database is reachable only inside Docker's private network
- **Startup ordering**: Compose waits for the database healthcheck before starting the app

## Project structure

```
.
├── main.py                  # FastAPI app (health + items endpoints)
├── requirements.txt         # Python dependencies
├── Dockerfile               # Multi-stage build (builder + runtime)
├── Dockerfile.singlestage   # Single-stage build, used only for size comparison
├── docker-compose.yml       # App + PostgreSQL services
├── .env.example             # Template for environment variables
├── .dockerignore            # Files excluded from the Docker build context
└── .gitignore               # Keeps .env and caches out of Git
```

## Prerequisites

- Docker with the Compose plugin (`docker compose`)

## Quick start

```bash
# 1. Create your environment file from the template
cp .env.example .env

# 2. Build and start both containers in the background
docker compose up --build -d

# 3. Check that both services are up (db should show "healthy")
docker compose ps
```

The API is then available at `http://localhost:8000`.

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/items -H "Content-Type: application/json" -d '{"name":"first item"}'
curl http://localhost:8000/items
```

## API endpoints

| Method | Path      | Description                                   |
|--------|-----------|-----------------------------------------------|
| GET    | `/health` | Checks that the app can reach the database    |
| POST   | `/items`  | Creates an item. Body: `{"name": "..."}`      |
| GET    | `/items`  | Lists all items                               |

Interactive API docs are available at `http://localhost:8000/docs`.

## How the Dockerfile works

1. **Builder stage**: starts from `python:3.11-slim`, installs the compiler and Postgres headers needed to build `psycopg2`, then installs the Python packages into a self-contained folder.
2. **Runtime stage**: starts again from a clean `python:3.11-slim`, installs only the Postgres runtime library, creates a non-root user, and copies in just the installed packages and `main.py` from the builder stage.

Because the runtime stage never inherits the builder's compilers or caches, the final image stays smaller.

## Environment variables

Copy `.env.example` to `.env` and adjust the values. The real `.env` file is excluded from Git (`.gitignore`) and from the Docker build context (`.dockerignore`).

| Variable            | Purpose                       |
|---------------------|-------------------------------|
| `POSTGRES_USER`     | Database user                 |
| `POSTGRES_PASSWORD` | Database password             |
| `POSTGRES_DB`       | Database name                 |

Compose builds the app's `DATABASE_URL` from these values at runtime.

## Image size comparison

```bash
docker build -t task2-multistage .
docker build -f Dockerfile.singlestage -t task2-singlestage .
docker images --filter "reference=task2-*"
```

`Dockerfile.singlestage` keeps everything in one stage and exists only for this comparison. Docker Compose does not use it.

## Cleanup

```bash
docker compose down      # stop and remove containers
docker compose down -v   # also remove the database volume
```