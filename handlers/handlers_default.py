from aiogram import Router, Bot
from aiogram.types import Message, CallbackQuery

router = Router()


@router.message()
async def default_message(message: Message):
    await message.answer("Действие невозможно, возможно стоит отменить предыдущее действие /cancel")


@router.callback_query()
async def default_callback(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    await bot.send_message(
        callback.from_user.id, "Действие невозможно, возможно стоит отменить предыдущее действие /cancel")
