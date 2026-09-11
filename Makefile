.PHONY: dev backend frontend migrate test lint clean

dev:
	docker compose up --build

dev-detach:
	docker compose up --build -d

backend:
	cd backend && uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

migrate:
	cd backend && alembic upgrade head

migrate-create:
	cd backend && alembic revision --autogenerate -m "$(msg)"

test:
	cd backend && pytest ../tests/backend/ -v --cov=app
	cd frontend && npm test

test-backend:
	cd backend && pytest ../tests/backend/ -v --cov=app

test-frontend:
	cd frontend && npm test

lint:
	cd backend && ruff check . && ruff format --check . && mypy app/
	cd frontend && npm run lint

format:
	cd backend && ruff check --fix . && ruff format .
	cd frontend && npx prettier --write src/

clean:
	docker compose down -v
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -rf backend/.ruff_cache backend/.mypy_cache
	rm -rf frontend/.next frontend/node_modules

install:
	cd backend && pip install -e ".[dev]"
	cd frontend && npm install

db-shell:
	docker compose exec db psql -U opendomain -d opendomain

cli:
	python -m backend.app.cli $(ARGS)
