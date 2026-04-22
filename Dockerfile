FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY bot ./bot
COPY core ./core
COPY db ./db
COPY services ./services
COPY integrations ./integrations
COPY scheduler ./scheduler
COPY api ./api
COPY scripts ./scripts
COPY migrations ./migrations
COPY alembic.ini ./

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir .

CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
