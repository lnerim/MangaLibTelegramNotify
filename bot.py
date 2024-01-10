import asyncio
import traceback
from datetime import datetime, UTC
from os import getenv

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BotCommand, ErrorEvent, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.media_group import MediaGroupBuilder

from api.enum import Lib, SITES
from api.enum.callback import SearchTitle, TitleData, NavigationData, ItemData
from api.requests import get_latest_updates
from api.requests.methods import search
from bot import BotDataBase
from bot.states import Search
from handlers import common

bot = Bot(token=getenv("TOKEN"))
dp = Dispatcher()
db = BotDataBase()
latest_updates: dict[str, datetime] = dict()


async def del_msg(state: FSMContext, user_id: int, *, msg: list[int] = None):
    messages = await state.get_data()
    if "del_msg" in messages:
        for m in messages["del_msg"]:
            await bot.delete_message(user_id, m)

    if msg is not None:
        await state.update_data(del_msg=msg)


@dp.message(StateFilter(None), Command(commands="new"))
async def cmd_new(message: Message, state: FSMContext):
    keyboard_new: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=site.name, callback_data=SearchTitle(site_id=site.site_id).pack())]
            for site in SITES.values()
        ]
    )
    await state.set_state(Search.wait_site)
    d_msg = await message.answer("Выберите сайт для добавления тайтла\nОтмена - /cancel", reply_markup=keyboard_new)
    await del_msg(state, message.from_user.id, msg=[d_msg.message_id])


@dp.callback_query(Search.wait_site, SearchTitle.filter())
async def callback_search(callback: CallbackQuery, state: FSMContext):
    data: SearchTitle = SearchTitle.unpack(callback.data)
    await state.set_state(Search.wait_input)
    await state.update_data(site_id=data.site_id)
    await callback.answer()
    d_msg = await callback.message.answer("Хорошо, теперь введите название произведения...\nОтмена - /cancel")
    await del_msg(state, callback.from_user.id, msg=[d_msg.message_id])


@dp.message(Search.wait_input, F.text != "/cancel")
async def search_input(message: Message, state: FSMContext):
    data = await state.get_data()
    site_id = data["site_id"]
    search_text = message.text

    search_msg = await message.answer("Поиск...")

    try:
        search_data = await search(site_id, search_text)
    except Exception as e:
        await search_msg.delete()
        await message.answer("Поиск не удался, попробуйте позже...")
        traceback.print_tb(e.__traceback__)
        return

    if not search_data:
        await search_msg.delete()
        research = await message.answer(f"Не удалось найти нужное произведение, попробуйте ввести название ещё раз...\n"
                                        f"Отмена - /cancel")
        await del_msg(state, message.from_user.id, msg=[research.message_id])
        await state.set_state(Search.wait_input)
        return

    album = MediaGroupBuilder()
    keyboard_input: list[list[InlineKeyboardButton]] = []

    names: dict[int, str] = dict()
    for num, title in enumerate(search_data[:10]):
        names[title.title_id] = title.rus_name
        album.add_photo(media=title.picture)
        keyboard_input.append([
            InlineKeyboardButton(
                text=title.rus_name,
                callback_data=TitleData(title_id=title.title_id, site_id=site_id).pack())
        ])

    await state.update_data(names=names)

    album_messages: list[Message] = await message.answer_media_group(media=album.build())
    d_msg = await message.answer("Выберите одно из найденных произведений\nОтмена - /cancel",
                                 reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_input))
    d_messages = [d_msg.message_id, *map(lambda x: x.message_id, album_messages)]

    await state.set_state(Search.choose_title)
    await search_msg.delete()
    await del_msg(state, message.from_user.id, msg=d_messages)


@dp.callback_query(Search.choose_title)
async def choose_title(callback: CallbackQuery, state: FSMContext):
    data: TitleData = TitleData.unpack(callback.data)
    name_data = await state.get_data()
    name = name_data["names"][int(data.title_id)]
    db.publication_add(data.title_id, callback.from_user.id, data.site_id, name)
    await bot.send_message(callback.from_user.id, "Успешно добавлено!")
    await del_msg(state, callback.from_user.id)
    await state.clear()


@dp.message(Command(commands="list"))
async def cmd_list(message: Message):
    try:
        builder = await keyboard(0, message.from_user.id)
        await message.answer(text="Список подписок", reply_markup=builder)
    except IndexError:
        await message.answer("Сейчас у Вас нет активных подписок, чтобы начать отслеживание, пожалуйста, "
                             "ознакомьтесь с инструкцией /help")


@dp.callback_query(NavigationData.filter())
async def callback_nav(callback: CallbackQuery):
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)

    data: NavigationData = NavigationData.unpack(callback.data)

    try:
        builder = await keyboard(data.page, callback.from_user.id)
        await bot.send_message(callback.from_user.id, text="Список подписок", reply_markup=builder)
    except IndexError:
        await bot.send_message(callback.from_user.id,
                               text="Сейчас у Вас нет активных подписок, чтобы начать отслеживание, "
                                    "пожалуйста, ""ознакомьтесь с инструкцией /help")
    finally:
        await callback.answer()


@dp.callback_query(ItemData.filter())
async def callback_nav(callback: CallbackQuery):

    data: ItemData = ItemData.unpack(callback.data)

    db.publication_delete(data.key)

    page = data.page
    while page >= 0:
        try:
            builder = await keyboard(page, callback.from_user.id)
            await bot.send_message(callback.from_user.id, text="Список подписок", reply_markup=builder)
            break
        except IndexError:
            page -= 1

    await callback.answer(f"Тайтл успешно удалён!")
    await bot.delete_message(callback.from_user.id, callback.message.message_id)


async def keyboard(page: int, user_id: int) -> InlineKeyboardMarkup:
    on_page = 10
    builder = InlineKeyboardBuilder()
    publications = db.publications_by_user(user_id)

    current_item = page * on_page
    current_publications = publications[current_item:current_item + on_page]
    if not current_publications:
        raise IndexError("Пустой список публикаций")

    for key, name in current_publications:
        builder.row(
            InlineKeyboardButton(
                text=name,
                callback_data=ItemData(key=key, page=page).pack()
            )
        )

    last_page = len(publications) // on_page
    navigation = []
    if page > 0:
        navigation.append(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=NavigationData(page=page-1).pack()
            )
        )
    if page < last_page:
        navigation.append(
            InlineKeyboardButton(
                text="Вперёд ➡️",
                callback_data=NavigationData(page=page+1).pack()
            )
        )
    builder.row(*navigation)
    return builder.as_markup()


@dp.message(Command(commands="cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await del_msg(state, message.from_user.id)
    await state.clear()
    await message.answer("Успешно отменено!")


async def check_update(site: Lib):
    await asyncio.sleep(int(site.site_id) * 10)

    latest_updates[site.site_id] = datetime.now(UTC)
    while True:
        try:
            latest_updates[site.site_id], titles = await get_latest_updates(site, latest_updates[site.site_id])
        except Exception as e:
            traceback.print_tb(e.__traceback__)
            await asyncio.sleep(30)
            continue

        for title in titles:
            users = db.users_by_publication(title_id=title.title_id)
            for _, user_id in users:
                try:
                    await bot.send_photo(
                        chat_id=user_id,
                        photo=title.picture,
                        caption=f"Вышло обновление в произведении: "
                                f"<a href='{site.url}{title.url}'>{title.rus_name or title.name}</a>",
                        parse_mode="HTML"
                    )
                except Exception as e:
                    traceback.print_tb(e.__traceback__)
                    await asyncio.sleep(30)
                    continue

        await asyncio.sleep(60 * 10)


async def set_commands():
    await bot.set_my_commands(commands=[
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Помощь по боту"),
        BotCommand(command="new", description="Добавить новый тайтл"),
        BotCommand(command="list", description="Активные подписки"),
    ])


@dp.error
async def error_message(event: ErrorEvent):
    traceback.print_tb(event.exception.__traceback__)


async def main():
    dp.include_router(common)

    await set_commands()
    async with asyncio.TaskGroup() as tg:
        tg.create_task(dp.start_polling(bot))

        for upd_site in SITES.values():
            tg.create_task(check_update(upd_site))


if __name__ == "__main__":
    asyncio.run(main())
