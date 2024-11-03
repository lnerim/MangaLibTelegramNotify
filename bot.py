import asyncio
from logging import Formatter, getLogger, INFO, StreamHandler
from logging.handlers import TimedRotatingFileHandler
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import BotCommand, ErrorEvent, User

from api.enum import SITES
from bot_utils.updater import check_update
from handlers import *


DEBUG_MODE = False

logger = getLogger()
formatter = Formatter("%(asctime)s %(levelname)s %(name)s [%(filename)s: %(lineno)d] %(message)s")
handler_file = TimedRotatingFileHandler(
    filename="bot.log",
    when="midnight",
    interval=1,
    backupCount=3,
    encoding="utf-8"
)
handler_file.setFormatter(formatter)
logger.addHandler(handler_file)
logger.setLevel(INFO)

if DEBUG_MODE:
    handler_console = StreamHandler()
    handler_console.setFormatter(formatter)
    logger.addHandler(handler_console)


bot = Bot(token=getenv("TOKEN"))
storage = RedisStorage.from_url(getenv("REDIS"))
dp = Dispatcher(storage=storage)


async def set_commands():
    await bot.set_my_commands(commands=[
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Помощь по боту"),
        BotCommand(command="new", description="Добавить новый тайтл"),
        BotCommand(command="list", description="Активные подписки"),
        BotCommand(command="cancel", description="Отменить действия"),
    ])


@dp.error()
@delete_messages
async def error_message(event: ErrorEvent, event_from_user: User):
    await bot.send_message(
        event_from_user.id,
        "Внутрення ошибка :(\n"
        "Обратитесь к разработчику, если ошибка возникает слишком часто"
    )
    logger.exception(event.exception)


async def main():
    logger.debug("Запуск...")

    dp.include_router(common)
    dp.include_router(title_add)
    dp.include_router(title_list)
    dp.include_router(default)

    await set_commands()
    async with asyncio.TaskGroup() as tg:
        tg.create_task(dp.start_polling(bot))

        for upd_site in SITES.values():
            tg.create_task(check_update(upd_site, bot))


if __name__ == "__main__":
    asyncio.run(main())
