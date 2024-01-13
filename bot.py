import asyncio
from logging import Formatter, getLogger, INFO
from logging.handlers import TimedRotatingFileHandler
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommand, ErrorEvent

from api.enum import SITES
from bot_utils.updater import check_update
from handlers import *
from handlers.del_msg import delete_messages

handler = TimedRotatingFileHandler(
    filename="bot.log",
    when="midnight",
    interval=1,
    backupCount=3,
    encoding="utf-8"
)
handler.setFormatter(
    Formatter("%(asctime)s %(levelname)s %(name)s [%(filename)s: %(lineno)d] %(message)s")
)
logger = getLogger()
logger.addHandler(handler)
logger.setLevel(INFO)


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


@dp.error()
@delete_messages
async def error_message(event: ErrorEvent, state: FSMContext):
    await state.clear()
    await event.update.message.answer(
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
