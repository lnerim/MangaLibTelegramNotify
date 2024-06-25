from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from api.enum import MangaLib, RanobeLib
from api.enum.lib import AnimeLib
from handlers import delete_messages

router = Router()
SUPPORTED = (f"<a href='{MangaLib.url}'>MangaLib</a>, "
             f"<a href='{RanobeLib.url}'>RanobeLib</a>, "
             f"<a href='{AnimeLib.url}'>AnimeLib</a>")


@router.message(Command(commands="start"))
async def cmd_start_private(message: Message):
    await message.answer(f"👋 Привет, {message.from_user.full_name}!\n\n"
                         f"🔄 Этот бот поможет тебе получать уведомления об обновлениях "
                         f"с сайтов семейства LIB прямо в Telegram.\n\n"
                         f"Поддерживаемые сайты: {SUPPORTED}.\n\n"
                         f"🆘 /help - получить справку по использованию бота",
                         disable_web_page_preview=True,
                         parse_mode=ParseMode.HTML)


@router.message(Command(commands="help"))
async def cmd_help(message: Message):
    await message.answer(f"1️⃣ Чтобы начать отслеживание тайтла, введите /new\n\n"
                         f"Вам будет предложено выбрать один из поддерживаемых сайтов: {SUPPORTED}. "
                         f"Остальные сайты могут начать поддерживаться, но целесообразность этого крайне мала.\n\n"
                         f"2️⃣ Далее нужно отправить боту название произведения, выберете нужное Вам и теперь при "
                         f"выходе новых обновлений сообщения будут приходить прямо в Телеграм.\n\n"
                         f"3️⃣ Чтобы узнать список своих подписок, введите /list\n\n"
                         f"Чтобы отписаться от конкретного тайтла, нажмите на кнопку с его названием в этом списке "
                         f"и подтвердите удаление.",
                         disable_web_page_preview=True,
                         parse_mode=ParseMode.HTML)


@router.message(Command(commands="cancel"))
@delete_messages
async def cmd_cancel(message: Message, state: FSMContext):
    state_data: dict = await state.get_data()
    if not state_data:
        await message.answer("🤷‍♂️ Никаких действий не было")
    else:
        await message.answer("✅ Успешно отменено!")
