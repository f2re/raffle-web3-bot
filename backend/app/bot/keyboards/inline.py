"""Inline keyboards for Telegram bot"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from app.config import settings


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Get main menu keyboard with Mini App button"""
    # TODO: Replace with actual Mini App URL
    webapp_url = "https://your-miniapp-url.com"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🎰 Открыть розыгрыши",
                web_app=WebAppInfo(url=webapp_url)
            )
        ],
        [
            InlineKeyboardButton(
                text="📊 Моя статистика",
                callback_data="stats"
            )
        ],
        [
            InlineKeyboardButton(
                text="ℹ️ Помощь",
                callback_data="help"
            )
        ]
    ])

    return keyboard
