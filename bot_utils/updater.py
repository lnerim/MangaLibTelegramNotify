import asyncio
import logging
from datetime import datetime, UTC

from aiogram import Bot

from api.enum import Lib
from api.requests import get_latest_updates
from bot_utils import db_new
from bot_utils.db import DBUpdates


async def check_update(site: Lib, bot: Bot):
    await asyncio.sleep(int(site.site_id) * 10)

    latest_updates: datetime = datetime.now(UTC)
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
            users: list[DBUpdates] = db_new.users_by_publication(title.title_id, title.site)
            for user in users:
                try:
                    await bot.send_photo(
                        chat_id=user.user_id,
                        photo=title.picture,
                        caption=f"Вышло обновление в произведении: "
                                f"<a href='{site.url}{title.url}'>{title.rus_name or title.name}</a>",
                        parse_mode="HTML"
                    )
                except Exception as e:
                    logging.exception(f"Пользователь {user.user_id} не получил обновление {title.slug=}")
                    logging.exception(e)
                    await asyncio.sleep(30)
                    continue

        await asyncio.sleep(60 * 10)
