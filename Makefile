.PHONY: up down logs test lint migrate seed shell

up:
	docker compose up --build

down:
	docker compose down -v

logs:
	docker compose logs -f api worker

migrate:
	docker compose exec api alembic upgrade head

seed:
	docker compose exec api python scripts/seed.py

test:
	pytest

lint:
	ruff check .

shell:
	docker compose exec api bash
