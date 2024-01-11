from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from handlers.del_msg import delete_messages

router = Router()


@router.message(Command(commands="start"))
async def cmd_start_private(message: Message):
    await message.answer(f"👋 Привет, {message.from_user.full_name}!\n\n"
                         f"🔄 Этот бот поможет тебе получать уведомления об обновлениях "
                         f"с сайтов семейства LIB прямо в Telegram.\n"
                         f"Чтобы получить справку по использованию бота, введите /help")


@router.message(Command(commands="help"))
async def cmd_help(message: Message):
    await message.answer(f"👀 Чтобы начать отслеживание тайтла, введите /new\n"
                         f"Чтобы узнать список своих подписок, введите /list, а чтобы удалить произведение, "
                         f"нажмите на кнопку с его названием в этом списке.",
                         parse_mode="HTML")


@router.message(Command(commands="cancel"))
@delete_messages
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Успешно отменено!")
