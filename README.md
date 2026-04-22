# CS2 Trading Assistant (Safe Semi-Auto MVP)

Telegram-бот для полуавтоматического трейдинга CS2-скинами: бот ищет и готовит сделки, но не исполняет опасные действия без явного approve владельца.

## Safety first
Проект **не** делает:
- обход Steam Guard / trade hold / подтверждений
- автоподтверждение мобильных трейдов
- headless/browser automation для скрытого управления аккаунтом
- несанкционированный scraping
- выдуманные private API
- silent execution без approve

## Architecture
- `bot/` — Telegram handlers, inline approve/reject flow
- `core/` — config/constants/logging
- `db/` — SQLAlchemy models, session, repositories
- `services/` — source routing, risk, scoring, pending actions, progress
- `integrations/` — market providers + execution adapters
- `scheduler/` — market scans and pending action creation
- `api/` — FastAPI health/ready/metrics
- `tests/` — pytest
- `migrations/` — Alembic

## Primary source policy
`cs_market` — primary source of truth.
Fallback используется только при включении `ENABLE_FALLBACK_SOURCES=true`.
Если primary недоступен и fallback выключен — сигнал/действие отклоняется.

## Approval workflow
1. Scanner находит кандидат.
2. Risk engine валидирует.
3. Создаётся `PendingAction`.
4. Бот отправляет карточку с кнопками Approve/Reject/Snooze/Blacklist.
5. После Approve:
   - если есть разрешённый execution adapter и он включён — выполняется
   - иначе перевод в `manual_required` + manual execution card

По умолчанию:
- `APPROVAL_REQUIRED=true`
- `AUTO_EXECUTE_AFTER_APPROVAL=false`
- `execution_mode=manual_only`

## Telegram commands
`/start /help /status /health /settings /balance /inventory /positions /deals /signals /risk /whitelist /blacklist /additem /removeitem /setprofit /setbudget /setmaxitem /scan /top /watchlist /pause /resume /logs /progress /pending /approve /reject /approve_last /reject_last`

## Environment
См. `.env.example`.
Секреты только через env.

## Run local
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev] --no-build-isolation
make run
```

Bot:
```bash
python -m bot.run_bot
```

## Docker
```bash
make up
make down
```

## API
- `GET /health`
- `GET /ready`
- `GET /metrics-summary`

## MVP limitations
- `CsMarketProvider` — безопасный адаптер-интерфейс, нужен подтверждённый публичный API contract.
- `ConfirmedExecutionAdapter` — заглушка; выключен по умолчанию.

## TODO
- полноценный settings wizard в Telegram
- детальный approval comments UX
- алерты только на улучшившиеся кандидаты
- полные alembic migrations для всех таблиц
