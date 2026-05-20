COMPOSE := docker compose
SERVICE := backend

.PHONY: dev install migrate test lint celery celery-beat shell db-shell

dev:
	$(COMPOSE) up --build

install:
	$(COMPOSE) build
	pip install -r requirements.txt

migrate:
	$(COMPOSE) run --rm $(SERVICE) python manage.py migrate

test:
	$(COMPOSE) run --rm $(SERVICE) python manage.py test

lint:
	$(COMPOSE) run --rm --no-deps $(SERVICE) sh -c "pip install -q ruff && ruff check ."

celery:
	$(COMPOSE) up celery

celery-beat:
	$(COMPOSE) up celery-beat

shell:
	$(COMPOSE) exec $(SERVICE) python manage.py shell

db-shell:
	$(COMPOSE) exec db psql -U postgres -d postgres
