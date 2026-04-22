"""Telegram bot runner."""

import asyncio

from aiogram import Bot, Dispatcher

from bot.handlers import router
from core.config import get_settings


async def main() -> None:
    settings = get_settings()
    if not settings.telegram_token:
        raise RuntimeError("TELEGRAM_TOKEN is required for bot runner")

    bot = Bot(token=settings.telegram_token)
    dispatcher = Dispatcher()
    dispatcher.include_router(router)
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
