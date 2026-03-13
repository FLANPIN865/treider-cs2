"""Telegram inline keyboards."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Запустить скан", callback_data="scan_start"), InlineKeyboardButton(text="Остановить скан", callback_data="scan_stop")],
            [InlineKeyboardButton(text="Топ сигналов", callback_data="top"), InlineKeyboardButton(text="Инвентарь", callback_data="inventory")],
            [InlineKeyboardButton(text="Риск", callback_data="risk"), InlineKeyboardButton(text="settings", callback_data="settings")],
            [InlineKeyboardButton(text="Watchlist", callback_data="watchlist"), InlineKeyboardButton(text="deals", callback_data="deals")],
            [InlineKeyboardButton(text="Прогресс до цели", callback_data="progress")],
        ]
    )
