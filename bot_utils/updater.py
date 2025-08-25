import asyncio
import logging
from datetime import datetime, UTC

from aiogram import Bot
from aiogram.types import URLInputFile

from api.enum import Lib, MediaItem
from api.requests import get_latest_updates
from bot_utils import db_new
from bot_utils.db import DBUpdates, DBMedia


async def check_update(site: Lib, bot: Bot):
    await asyncio.sleep(int(site.site_id) * 10 + 30)

    latest_updates: datetime = datetime.now(UTC)
    logging.info(f"Начало обновления {site.name} {latest_updates=!s}")
    while True:
        try:
            latest_updates, titles = await get_latest_updates(site, latest_updates)
            logging.info(f"Получено обновление {site.name} {latest_updates=!s} {len(titles)=}")
        except Exception as e:
            logging.exception(f"Обновление {site.name} не получено")
            logging.exception(e)
            await asyncio.sleep(30)
            continue

        for title in titles:
            users: list[DBUpdates] = await db_new.users_by_publication(title.title_id, title.site)
            db_title: DBMedia = await db_new.publication_get(title.title_id, title.site)
            for user in users:
                item: MediaItem

                disable_notification = title.latest_items[0] % db_title

                for item in title.latest_items:
                    try:
                        await bot.send_photo(
                            chat_id=user.user_id,
                            photo=URLInputFile(title.picture),
                            caption=f"{"⭐️" if disable_notification else "🌟"} "
                                    f"Вышло обновление в произведении: "
                                    f"<a href='{site.url}{title.url}'>{title.rus_name or title.name}</a>\n\n"
                                    f"{item:info}",
                            parse_mode="HTML",
                            disable_notification=disable_notification
                        )
                        disable_notification = True
                    except Exception as e:
                        logging.exception(f"Пользователь {user.user_id} не получил обновление {title.slug=}")
                        logging.exception(e)
                        await asyncio.sleep(30)
                        continue

            # True (без звука) - обновление не нужно
            # False (со звуком) - обновление нужно
            if not title.latest_items[0] % db_title:
                await db_new.publication_update(
                    title.title_id, title.site_id,
                    title.latest_items[0].major, title.latest_items[0].minor
                )

        await asyncio.sleep(60 * 10)
