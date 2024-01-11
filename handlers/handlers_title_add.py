import traceback

from aiogram import Router, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.media_group import MediaGroupBuilder

from api.enum import SITES
from api.enum.callback import SearchTitle, TitleData
from api.requests import search
from bot_utils import db
from bot_utils.states import Search
from handlers.del_msg import delete_messages

router = Router()


@router.message(StateFilter(None), Command(commands="new"))
@delete_messages
async def cmd_new(message: Message, state: FSMContext, to_delete: list):
    keyboard_new: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=site.name, callback_data=SearchTitle(site_id=site.site_id).pack())]
            for site in SITES.values()
        ]
    )
    await state.set_state(Search.wait_site)
    d_msg = await message.answer("Выберите сайт для добавления тайтла\nОтмена - /cancel", reply_markup=keyboard_new)
    to_delete.append(d_msg)


@router.callback_query(Search.wait_site, SearchTitle.filter())
@delete_messages
async def callback_search(callback: CallbackQuery, state: FSMContext, to_delete: list):
    data: SearchTitle = SearchTitle.unpack(callback.data)
    await state.set_state(Search.wait_input)
    await state.update_data(site_id=data.site_id)
    await callback.answer()
    d_msg = await callback.message.answer("Хорошо, теперь введите название произведения...\nОтмена - /cancel")
    to_delete.append(d_msg)


@router.message(Search.wait_input)
@delete_messages
async def search_input(message: Message, state: FSMContext, to_delete: list):
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
        to_delete.append(research)
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

    await state.set_state(Search.choose_title)
    await search_msg.delete()

    to_delete.append(d_msg)
    to_delete += album_messages


@router.callback_query(Search.choose_title)
@delete_messages
async def choose_title(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data: TitleData = TitleData.unpack(callback.data)
    name_data = await state.get_data()
    name = name_data["names"][int(data.title_id)]
    db.publication_add(data.title_id, callback.from_user.id, data.site_id, name)
    await bot.send_message(callback.from_user.id, "Успешно добавлено!")
    await state.clear()
