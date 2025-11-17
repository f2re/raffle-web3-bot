"""Start command handler"""

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from app.bot.keyboards.inline import get_main_menu_keyboard


router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Handle /start command"""
    welcome_text = (
        "🎯 <b>Добро пожаловать в Web3 Raffle Bot!</b>\n\n"
        "Участвуйте в провабельно честных розыгрышах на TON blockchain.\n\n"
        "<b>Доступные розыгрыши:</b>\n"
        "🚀 <b>Экспресс</b> - 5 участников, 1 TON, розыгрыш через 1 минуту\n"
        "⭐ <b>Стандарт</b> - 10 участников, 2 TON, розыгрыш через 2 минуты\n"
        "💎 <b>Премиум</b> - 30 участников, 5 TON, розыгрыш через 5 минут\n\n"
        "Нажмите кнопку ниже, чтобы начать!"
    )

    await message.answer(
        welcome_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "help")
async def callback_help(callback: CallbackQuery):
    """Handle help button"""
    help_text = (
        "❓ <b>Как это работает:</b>\n\n"
        "1️⃣ Выберите розыгрыш и подключите TON кошелек\n"
        "2️⃣ Оплатите участие через TON Connect\n"
        "3️⃣ Дождитесь набора участников\n"
        "4️⃣ Победитель выбирается через Random.org (провабельно честно!)\n"
        "5️⃣ Приз автоматически отправляется победителю\n\n"
        "<b>Комиссия:</b> 10% с призового фонда\n"
        "<b>Проверка честности:</b> Каждый розыгрыш имеет подпись Random.org"
    )

    await callback.answer()
    await callback.message.answer(help_text, parse_mode="HTML")


@router.callback_query(F.data == "stats")
async def callback_stats(callback: CallbackQuery):
    """Handle stats button"""
    # TODO: Get user stats from database
    stats_text = (
        "📊 <b>Ваша статистика:</b>\n\n"
        "Участий: 0\n"
        "Побед: 0\n"
        "Потрачено: 0 TON\n"
        "Выиграно: 0 TON"
    )

    await callback.answer()
    await callback.message.answer(stats_text, parse_mode="HTML")
