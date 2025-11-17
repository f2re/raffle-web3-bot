"""Notification handlers"""

from aiogram import Bot
from loguru import logger


async def notify_winner(bot: Bot, telegram_id: int, prize_amount: float, raffle_type: str):
    """Notify winner about their prize"""
    try:
        message = (
            f"🎉 <b>Поздравляем! Вы выиграли!</b>\n\n"
            f"Розыгрыш: {raffle_type.upper()}\n"
            f"Приз: <b>{prize_amount} TON</b>\n\n"
            f"Приз автоматически отправлен на ваш кошелек!"
        )

        await bot.send_message(
            chat_id=telegram_id,
            text=message,
            parse_mode="HTML"
        )

        logger.info(f"Sent winner notification to {telegram_id}")

    except Exception as e:
        logger.error(f"Failed to send winner notification: {e}")


async def notify_raffle_started(bot: Bot, telegram_id: int, raffle_type: str, minutes: int):
    """Notify participant that raffle timer started"""
    try:
        message = (
            f"⏱ <b>Розыгрыш {raffle_type.upper()} начинается!</b>\n\n"
            f"Набрано минимальное количество участников.\n"
            f"Розыгрыш через: {minutes} минут"
        )

        await bot.send_message(
            chat_id=telegram_id,
            text=message,
            parse_mode="HTML"
        )

        logger.info(f"Sent raffle started notification to {telegram_id}")

    except Exception as e:
        logger.error(f"Failed to send raffle started notification: {e}")
