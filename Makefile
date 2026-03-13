run:
	uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload

test:
	pytest -q

lint:
	ruff check .

format:
	black .

migrate:
	alembic upgrade head

up:
	docker compose up --build -d

down:
	docker compose down
