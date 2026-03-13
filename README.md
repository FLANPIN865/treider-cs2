# CS2 Trading Assistant (MVP)

Безопасный Telegram-ассистент для анализа CS2 скинов и поиска торговых возможностей.

## Что делает MVP

> ⚠️ Для офлайн-CI в этом репозитории отключена автоустановка зависимостей в `pip install -e .[dev]`.
> Для реального запуска установите стек вручную: `aiogram`, `fastapi`, `sqlalchemy`, `alembic`, `psycopg`, `pydantic-settings`, `httpx`, `loguru`, `apscheduler`.

- собирает рыночные данные через `MarketDataProvider`
- `cs_market` задан как primary source of truth
- использует fallback-источник только при недоступности primary (если включено)
- считает спред/комиссии/ожидаемую прибыль
- применяет risk engine и блокирует небезопасные сигналы
- хранит инвентарь/позиции/сделки/сигналы/аудит
- показывает прогресс к цели `Butterfly Knife`
- предоставляет FastAPI health/ready/metrics endpoints

## Архитектура
- `bot/` — Telegram handlers, keyboards, formatters
- `core/` — config, logging, constants
- `db/` — SQLAlchemy models, session, repositories
- `services/` — risk engine, routing, scoring, progress
- `integrations/` — адаптеры источников цен
- `scheduler/` — APScheduler market scan jobs
- `api/` — FastAPI
- `migrations/` — Alembic
- `tests/` — pytest
- `scripts/` — seed data

## Telegram команды
`/start /help /status /health /settings /balance /inventory /positions /deals /signals /risk /whitelist /blacklist /additem /removeitem /setprofit /setbudget /setmaxitem /scan /top /watchlist /pause /resume /logs /progress`

Inline-кнопки:
- Запустить скан
- Остановить скан
- Топ сигналов
- Инвентарь
- Риск
- Настройки
- Watchlist
- Последние сделки
- Прогресс до цели

## Важные ограничения безопасности
- нет обхода trade hold
- нет автоподтверждения трейдов
- нет browser automation для Steam
- нет скрытой автоматизации аккаунта
- нет выдуманных private API endpoint-ов

## Настройка окружения
1. Скопируйте `.env.example` → `.env`
2. Укажите `TELEGRAM_TOKEN`, `TELEGRAM_OWNER_IDS`, `DATABASE_URL`
3. При наличии публичного API CS Market укажите `CS_MARKET_BASE_URL` и `CS_MARKET_API_KEY`

## Локальный запуск
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
make run
```

Запуск Telegram-бота:
```bash
python -m bot.run_bot
```

## Docker
```bash
make up
make down
```

## Миграции
```bash
make migrate
```

## Seed
```bash
python scripts/seed_data.py
```

## Пример сценария
1. Добавить предметы в watchlist (seed already includes defaults).
2. Запустить скан `/scan`.
3. Просмотреть `/signals` и `/top`.
4. Проверить прогресс `/progress` до Butterfly Knife.

## MVP ограничения
- `CsMarketProvider` содержит TODO для реального подтверждённого API-контракта.
- Уведомления Telegram о сигналах в текущем MVP представлены как готовая логика форматирования + job orchestration.

## TODO v2
- полноценный stateful Telegram settings wizard
- idempotent Alembic migrations for all tables
- Prometheus metrics
- richer anti-spam and RBAC
- webhook mode for Telegram bot
