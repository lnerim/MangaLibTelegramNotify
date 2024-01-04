import asyncio
import traceback
from datetime import datetime, UTC
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, ErrorEvent

from api.enum import Lib, SITES
from api.requests import get_latest_updates
from bot import BotDataBase

bot = Bot(token=getenv("TOKEN"))
dp = Dispatcher()
db = BotDataBase()
latest_updates: dict[str, datetime] = dict()


async def check_update(site: Lib):
    await asyncio.sleep(int(site.site_id) * 5)
    latest_updates[site.site_id] = datetime.now(UTC)

    while True:
        try:
            titles = await get_latest_updates(site)
        except Exception as e:
            traceback.print_tb(e.__traceback__)
            await asyncio.sleep(30)
            continue

        print(datetime.now(UTC))
        print(", ".join(map(lambda x: x.name, titles)))

        for title in titles:
            if title.last_item_at <= latest_updates[site.site_id]:
                latest_updates[site.site_id] = titles[0].last_item_at or datetime.now(UTC)
                break

            users = db.users_by_publication(title_id=title.title_id)
            for _, user_id in users:
                try:
                    await bot.send_photo(
                        chat_id=user_id,
                        photo=title.picture,
                        caption=f"Вышло обновление в произведении: "
                                f"<a href='{site.url}{title.url}'>{title.rus_name}</a>",
                        parse_mode="HTML"
                    )
                except Exception as e:
                    traceback.print_tb(e.__traceback__)
                    await asyncio.sleep(30)
                    continue

        await asyncio.sleep(10 * 60)


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
    await set_commands()
    async with asyncio.TaskGroup() as tg:
        for upd_site in SITES.values():
            tg.create_task(check_update(upd_site))

        tg.create_task(dp.start_polling(bot))


if __name__ == "__main__":
    asyncio.run(main())
