from aiogram import Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

router = Router()


@router.message()
async def default_message(message: Message, state: FSMContext):
    current_state = await state.get_state()
    await message.answer(text_by_state(current_state))


@router.callback_query()
async def default_callback(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    current_state = await state.get_state()
    await bot.send_message(callback.from_user.id, text_by_state(current_state))


def text_by_state(current_state: str) -> str:
    match current_state:
        case None:
            return "Не знаешь что делать?\nЕсть мануал /help\nДобавить новый тайтл /new"
        case s if s.startswith("Search"):
            return "В данный момент вы добавляете новый тайтл.\nОтменить поиск /cancel"
        case _:
            return "Действие невозможно, возможно стоит отменить предыдущее действие /cancel"
