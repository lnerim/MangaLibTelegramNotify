import asyncio
from datetime import datetime, UTC
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BotCommand, ErrorEvent, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.media_group import MediaGroupBuilder

from api.enum import Lib, MangaLib, RanobeLib, SITES
from api.enum.callback import SearchTitle, TitleData, NavigationData, ItemData
from api.requests import get_latest_updates
from api.requests.methods import search
from bot import BotDataBase
from bot.states import Search

bot = Bot(token=getenv("TOKEN"))
dp = Dispatcher()
db = BotDataBase()
latest_updates: dict[str, datetime] = dict()


@dp.message(Command(commands="start"))
async def cmd_start_private(message: Message):
    await message.answer(f"👋 Привет, {message.from_user.full_name}!\n\n"
                         f"🔄 Этот бот поможет тебе получать уведомления об обновлениях "
                         f"с сайтов семейства LIB прямо в Telegram.\n"
                         f"Чтобы получить справку по использованию бота, введите /help")


@dp.message(Command(commands="help"))
async def cmd_help(message: Message):
    await message.answer(f"👀 Чтобы начать отслеживание тайтла, введите /new\n"
                         f"Чтобы узнать список своих подписок, введите /list, а чтобы удалить произведение, "
                         f"нажмите на кнопку с его названием в этом списке.",
                         parse_mode="HTML")


@dp.message(StateFilter(None), Command(commands="new"))
async def cmd_new(message: Message, state: FSMContext):
    keyboard_new: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=site.name, callback_data=SearchTitle(site_id=site.site_id).pack())]
            for site in SITES.values()
        ]
    )
    await state.set_state(Search.wait_site)
    await message.answer("Выберите сайт для добавления тайтла\nОтмена - /cancel", reply_markup=keyboard_new)


@dp.callback_query(Search.wait_site, SearchTitle.filter())
async def callback_search(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    data: SearchTitle = SearchTitle.unpack(callback.data)
    await state.set_state(Search.wait_input)
    await state.update_data(site_id=data.site_id)
    await callback.answer()
    await callback.message.answer("Хорошо, теперь введите название произведения...\nОтмена - /cancel")


@dp.message(Search.wait_input)
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
        print(e.__traceback__)
        return

    if not search_data:
        await message.answer(f"Не удалось найти нужное произведение, попробуйте ввести название ещё раз...")
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

    await search_msg.delete()

    await message.answer_media_group(media=album.build())
    await message.answer("Выберите одно из найденных произведений\nОтмена - /cancel",
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_input))
    await state.set_state(Search.choose_title)


@dp.callback_query(Search.choose_title)
async def choose_title(callback: CallbackQuery, state: FSMContext):
    data: TitleData = TitleData.unpack(callback.data)
    name_data = await state.get_data()
    name = name_data["names"][int(data.title_id)]
    db.publication_add(data.title_id, callback.from_user.id, data.site_id, name)
    await callback.answer("Успешно добавлено!")
    await callback.message.delete()
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
        builder = await keyboard(data.page, data.user_id)
        await bot.send_message(data.user_id, text="Список подписок", reply_markup=builder)
    except IndexError:
        await bot.send_message(data.user_id,
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
            await bot.send_message(data.user_id, text="Список подписок", reply_markup=builder)
            break
        except IndexError:
            page -= 1

    await callback.answer(f"Тайтл успешно удалён!")
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)


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
    await state.clear()
    await message.answer("Успешно отменено!")
    await message.delete()


async def check_update(site: Lib):
    sleep_time = 10 * 60 + int(site.site_id)  # 10 минут + время от id сайта для минимизации запросов в одно время
    latest_updates[site.site_id] = datetime.now(UTC)
    while True:
        try:
            titles = await get_latest_updates(site)
        except Exception as e:
            print(e.__traceback__)
            continue

        for title in titles:
            if title.last_item_at < latest_updates[site.site_id]:
                latest_updates[site.site_id] = title.last_item_at if not None else datetime.now()
                break
            users = db.users_by_publication(title_id=title.title_id)
            try:
                for _, user_id in users:
                    await bot.send_photo(
                        chat_id=user_id,
                        photo=title.picture,
                        caption=f"Вышло обновление в произведении: "
                                f"<a href='{site.url}{title.url}'>{title.rus_name}</a>",
                        parse_mode="HTML"
                    )
            except Exception as e:
                print(e.__traceback__)
                continue

        await asyncio.sleep(sleep_time)


async def set_commands():
    await bot.set_my_commands(commands=[
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Помощь по боту"),
        BotCommand(command="new", description="Добавить новый тайтл"),
        BotCommand(command="list", description="Активные подписки"),
    ])


@dp.error
async def error_message(event: ErrorEvent):
    print(event.error_message)


async def main():
    await set_commands()
    async with asyncio.TaskGroup() as tg:
        tg.create_task(check_update(MangaLib))
        tg.create_task(check_update(RanobeLib))

        task0 = tg.create_task(dp.start_polling(bot))

        task0.add_done_callback(
            lambda: map(lambda x: x.cancel(), asyncio.all_tasks(task0.get_loop()))
        )


if __name__ == "__main__":
    asyncio.run(main())
