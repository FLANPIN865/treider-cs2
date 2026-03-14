"""Telegram inline keyboards."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Запустить скан", callback_data="scan_start"), InlineKeyboardButton(text="Остановить скан", callback_data="scan_stop")],
            [InlineKeyboardButton(text="Топ сигналов", callback_data="top"), InlineKeyboardButton(text="Pending actions", callback_data="pending")],
            [InlineKeyboardButton(text="Approve", callback_data="approve_last"), InlineKeyboardButton(text="Reject", callback_data="reject_last")],
            [InlineKeyboardButton(text="Snooze", callback_data="snooze_last"), InlineKeyboardButton(text="Blacklist item", callback_data="blacklist_last")],
            [InlineKeyboardButton(text="Inventory", callback_data="inventory"), InlineKeyboardButton(text="Risk", callback_data="risk")],
            [InlineKeyboardButton(text="Settings", callback_data="settings"), InlineKeyboardButton(text="Progress to target", callback_data="progress")],
        ]
    )


def action_keyboard(action_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Approve", callback_data=f"approve:{action_id}"), InlineKeyboardButton(text="Reject", callback_data=f"reject:{action_id}")],
            [InlineKeyboardButton(text="Snooze", callback_data=f"snooze:{action_id}"), InlineKeyboardButton(text="Blacklist item", callback_data=f"blacklist:{action_id}")],
        ]
    )
