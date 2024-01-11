import asyncio
import traceback
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, ErrorEvent

from api.enum import SITES
from bot_utils.updater import check_update
from handlers import *

bot = Bot(token=getenv("TOKEN"))
dp = Dispatcher()


async def set_commands():
    await bot.set_my_commands(commands=[
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Помощь по боту"),
        BotCommand(command="new", description="Добавить новый тайтл"),
        BotCommand(command="list", description="Активные подписки"),
        BotCommand(command="cancel", description="Отменить действия"),
    ])


@dp.error
async def error_message(event: ErrorEvent):
    traceback.print_tb(event.exception.__traceback__)


async def main():
    dp.include_router(common)
    dp.include_router(title_add)
    dp.include_router(title_list)

    await set_commands()
    async with asyncio.TaskGroup() as tg:
        tg.create_task(dp.start_polling(bot))

        for upd_site in SITES.values():
            tg.create_task(check_update(upd_site, bot))


if __name__ == "__main__":
    asyncio.run(main())
