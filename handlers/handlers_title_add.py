import logging

from aiogram import Router, Bot
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.media_group import MediaGroupBuilder

from api.enum import SITES, TitleInfo
from api.enum.callback import SearchTitle, TitleData
from api.requests import search, more_info
from bot_utils import db_new
from bot_utils.states import Search
from handlers import delete_messages

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
    d_msg = await message.answer("📌 Выберите сайт для добавления тайтла\nОтмена - /cancel", reply_markup=keyboard_new)
    to_delete.append(d_msg)


@router.callback_query(Search.wait_site, SearchTitle.filter())
@delete_messages
async def callback_search(callback: CallbackQuery, state: FSMContext, to_delete: list):
    data: SearchTitle = SearchTitle.unpack(callback.data)
    await state.set_state(Search.wait_input)
    await state.update_data(site_id=data.site_id)
    await callback.answer()
    d_msg = await callback.message.answer("📌 Хорошо, теперь введите название произведения...\nОтмена - /cancel")
    to_delete.append(d_msg)


@router.message(Search.wait_input)
@delete_messages
async def search_input(message: Message, state: FSMContext, to_delete: list):
    data = await state.get_data()
    site_id = data["site_id"]
    search_text = message.text

    search_msg = await message.answer("🔍 Поиск...")

    try:
        search_data = await search(site_id, search_text)
    except Exception as e:
        await message.answer("🔍 Поиск не удался, попробуйте позже...")
        logging.exception(e)
        return
    finally:
        await search_msg.delete()

    if not search_data:
        research = await message.answer("🔍 Не удалось найти нужное произведение, "
                                        "попробуйте ввести название ещё раз...\n"
                                        "Отмена - /cancel")
        to_delete.append(research)
        await state.set_state(Search.wait_input)
        return

    album = MediaGroupBuilder()
    keyboard_input: list[list[InlineKeyboardButton]] = []

    slugs: dict[int, str] = dict()
    names: dict[int, str] = dict()
    for num, title in enumerate(search_data[:10]):
        slugs[title.title_id] = title.slug
        names[title.title_id] = title.rus_name or title.name
        album.add_photo(media=title.picture)
        keyboard_input.append([
            InlineKeyboardButton(
                text=title.rus_name or title.name,
                callback_data=TitleData(title_id=title.title_id, site_id=site_id).pack())
        ])

    await state.update_data(slugs=slugs)
    await state.update_data(names=names)

    album_messages: list[Message] = await message.answer_media_group(media=album.build())
    d_msg = await message.answer("📌 Выберите одно из найденных произведений\nОтмена - /cancel",
                                 reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_input))

    await state.set_state(Search.choose_title)

    to_delete.append(d_msg)
    to_delete += album_messages


@router.callback_query(Search.choose_title)
@delete_messages
async def choose_title(callback: CallbackQuery, state: FSMContext, bot: Bot, to_delete: list):
    title_data: TitleData = TitleData.unpack(callback.data)
    state_data = await state.get_data()
    slug = state_data["slugs"][title_data.title_id]

    info_msg = await bot.send_message(callback.from_user.id, "Загрузка информации...")
    try:
        t: TitleInfo = await more_info(title_data.site_id, slug)
    except Exception as e:
        logging.exception(f"Ошибка получения расширенной информации о тайтле {title_data.site_id=} {slug}")
        logging.exception(e)
        await bot.send_message(callback.from_user.id, "Ошибка загрузки дополнительной информации...")
        # Основная информация известна, добавляем без показа расширенной информации
        await add_title(callback, state, bot)
        return
    finally:
        await info_msg.delete()

    caption = f"<i>{t.rus_name or t.name}</i>\n"\
              f"<b>Возрастное ограничение:</b> {t.ageRestriction} <b>Рейтинг:</b> {t.rating}\n"\
              f"<b>Тип:</b> {t.type}\n"\
              f"{t.releaseDateString} {t.status}\n"\
              f"<b>Авторство:</b> {', '.join(t.authors)}\n"\
              f"<b>Жанры:</b> {', '.join(t.genres)}\n"\
              f"<b>Теги:</b> {', '.join(t.tags)}\n\n"

    len_to_summary = 1024 - len(caption) - 19
    summary = t.summary[:len_to_summary - 3] + "..." if len(t.summary) > len_to_summary else t.summary

    d_msg = await bot.send_photo(
        chat_id=callback.from_user.id,
        photo=t.picture,
        caption=caption + summary + f"\n\nОтменить: /cancel",  # cancel len = 19
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(
                    text="✏️ Добавить",
                    callback_data=TitleData(title_id=t.title_id, site_id=title_data.site_id).pack())
            ]]
        )
    )
    to_delete.append(d_msg)

    await state.set_state(Search.add_title)


@router.callback_query(Search.add_title)
@delete_messages
async def add_title_handler(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await add_title(callback, state, bot)


async def add_title(callback: CallbackQuery, state: FSMContext, bot: Bot):
    title_data: TitleData = TitleData.unpack(callback.data)
    name_data = await state.get_data()
    name = name_data["names"][title_data.title_id]

    await db_new.publication_add(callback.from_user.id, int(title_data.title_id), title_data.site_id, name)

    await bot.send_message(callback.from_user.id, "✅ Успешно добавлено!\nСписок подписок /list")
