# PayPulse

Django backend for invoice and payment workflows, with PostgreSQL, Redis, and Celery.

## Prerequisites

| Tool | Purpose |
|------|---------|
| [Docker](https://docs.docker.com/get-docker/) & Docker Compose | Run the full stack (recommended) |
| [uv](https://docs.astral.sh/uv/) | Local Python env and dependency management |
| [Make](https://www.gnu.org/software/make/) | Shortcuts for Docker workflows (`backend/` only) |

Python **3.12+** is required for local development with uv.

---

## Quick start with Docker

All commands below are run from the `backend/` directory.

### 1. Clone and configure environment

```bash
git clone <repository-url>
cd paypulse/backend
cp .env.example .env
```

Edit `.env` and set your secrets (Django key, API keys, etc.). Defaults work for local Postgres and Redis via Docker Compose.

### 2. Build images and start services

```bash
make install   # docker compose build + local pip install (optional, for IDE)
make dev       # start db, redis, backend, celery, celery-beat
```

In another terminal (with the stack running):

```bash
make migrate
```

The API is available at **http://localhost:8000**.

### 3. Optional: run Celery in separate terminals

If you prefer not to run workers via `make dev`, use:

```bash
make celery       # worker
make celery-beat  # scheduler
```

---

## Local development with uv

Use uv when you want dependencies in a virtualenv on your machine (IDE support, faster iteration) while still using Docker for Postgres and Redis.

### 1. Install uv

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# or Homebrew
brew install uv
```

### 2. Install Python dependencies

From the **repository root** (where `pyproject.toml` and `uv.lock` live):

```bash
cd paypulse
uv sync
```

This creates `.venv` and installs locked dependencies.

### 3. Configure environment

```bash
cp backend/.env.example backend/.env
```

For local Django against Dockerized Postgres/Redis, ensure these point at **localhost** (not Docker service names):

```env
DATABASE_URL=postgres://postgres:postgres@localhost:5432/postgres
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### 4. Start infrastructure only

```bash
cd backend
docker compose up -d db redis
```

### 5. Run Django with uv

From `backend/` (uv finds the root `pyproject.toml` automatically):

```bash
uv run python manage.py migrate
uv run python manage.py runserver
```

Run Celery locally in separate terminals:

```bash
uv run celery -A config worker -l info
uv run celery -A config beat -l info
```

---

## Makefile reference

Run from `backend/`:

| Command | Description |
|---------|-------------|
| `make dev` | `docker compose up --build` — full stack |
| `make install` | Build Docker images; `pip install -r requirements.txt` locally |
| `make migrate` | Apply database migrations |
| `make test` | Run Django tests |
| `make lint` | Run Ruff via Docker |
| `make celery` | Start Celery worker |
| `make celery-beat` | Start Celery beat |
| `make shell` | Django shell (`manage.py shell`) |
| `make db-shell` | PostgreSQL CLI (`psql`) |
