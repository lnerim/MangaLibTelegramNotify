from aiogram import Bot, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from api.enum.callback import NavigationData, ItemData, ItemDataDelete
from bot_utils import db_new
from bot_utils.db import DBUpdates, DBMedia

router = Router()


@router.message(Command(commands="list"))
async def cmd_list(message: Message):
    try:
        builder = await keyboard(0, message.from_user.id)
        await message.answer(text="📌 Список подписок\nЧтобы удалить тайтл, выберите его из списка",
                             reply_markup=builder)
    except IndexError:
        await message.answer("📪 Сейчас у Вас нет активных подписок, чтобы начать отслеживание, "
                             "пожалуйста, ознакомьтесь с инструкцией /help")


@router.callback_query(NavigationData.filter())
async def callback_nav(callback: CallbackQuery, bot: Bot):
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)

    data: NavigationData = NavigationData.unpack(callback.data)

    try:
        builder = await keyboard(data.page, callback.from_user.id)
        await bot.send_message(callback.from_user.id,
                               text="📌 Список подписок\nЧтобы удалить тайтл, выберите его из списка",
                               reply_markup=builder)
    except IndexError:
        await bot.send_message(callback.from_user.id,
                               text="📪 Сейчас у Вас нет активных подписок, чтобы начать отслеживание, "
                                    "пожалуйста, ознакомьтесь с инструкцией /help")
    finally:
        await callback.answer()


@router.callback_query(ItemData.filter())
async def callback_item(callback: CallbackQuery):
    await callback.message.delete()
    data: ItemData = ItemData.unpack(callback.data)

    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="🗑 Да",
            callback_data=ItemDataDelete(item_id=data.item_id, site_id=data.site_id,
                                         page=data.page, delete=True).pack()
        )
    )
    builder.add(
        InlineKeyboardButton(
            text="💾 Нет",
            callback_data=ItemDataDelete(item_id=data.item_id, site_id=data.site_id,
                                         page=data.page, delete=False).pack()
        )
    )

    title: DBMedia = await db_new.publication_get(data.item_id, data.site_id)
    await callback.message.answer(text=f"❌ Удалить <b>{title.media_name}</b> из списка отслеживаемых?",
                                  parse_mode=ParseMode.HTML,
                                  reply_markup=builder.as_markup())


@router.callback_query(ItemDataDelete.filter())
async def callback_nav(callback: CallbackQuery, bot: Bot):
    data: ItemDataDelete = ItemDataDelete.unpack(callback.data)

    if data.delete:
        await db_new.publication_delete(callback.from_user.id, data.item_id, data.site_id)
        await callback.answer("Тайтл успешно удалён!")
    else:
        await callback.answer("Тайтл не удалён")

    page = data.page
    while page >= 0:
        try:
            builder = await keyboard(page, callback.from_user.id)
            await bot.send_message(callback.from_user.id,
                                   text="📌 Список подписок\nЧтобы удалить тайтл, выберите его из списка",
                                   reply_markup=builder)
            break
        except IndexError:
            if page == 0:
                await bot.send_message(callback.from_user.id,
                                       text="📪 Сейчас у Вас нет активных подписок, чтобы начать отслеживание, "
                                            "пожалуйста, ознакомьтесь с инструкцией /help")
            page -= 1

    await bot.delete_message(callback.from_user.id, callback.message.message_id)


async def keyboard(page: int, user_id: int) -> InlineKeyboardMarkup:
    on_page = 10
    builder = InlineKeyboardBuilder()
    publications: list[DBUpdates] = await db_new.publications_by_user(user_id)

    current_item = page * on_page
    current_publications: list[DBUpdates] = publications[current_item:current_item + on_page]
    if not current_publications:
        raise IndexError("Пустой список публикаций")

    for p in current_publications:
        media = await db_new.publication_get(p.media_id, p.site_id)
        builder.row(
            InlineKeyboardButton(
                text=media.media_name,
                callback_data=ItemData(item_id=p.media_id, site_id=p.site_id, page=page).pack()
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
    if page < last_page and on_page * (page + 1) != len(publications):
        navigation.append(
            InlineKeyboardButton(
                text="Вперёд ➡️",
                callback_data=NavigationData(page=page+1).pack()
            )
        )
    builder.row(*navigation)
    return builder.as_markup()
