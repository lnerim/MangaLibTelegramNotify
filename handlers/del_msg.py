import asyncio
import inspect
import logging
from asyncio import TaskGroup, Task

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, User


def delete_messages(func: callable) -> callable:
    async def wrapper(*args, **kwargs) -> None:
        state, state_data, user_id, bot = await get_user_data(**kwargs)

        await timer_del(state_data)

        await messages_del(state_data, user_id, bot)

        to_delete: list[Message] = []
        kwargs["to_delete"] = to_delete

        await func(*args, **get_new_kwargs(func, kwargs))

        if to_delete:
            await state.update_data(del_msg=to_delete)
            await timer_set(state, bot, user_id)
        else:
            await state.clear()

    return wrapper


async def delete_messages_after_long_time(state: FSMContext, bot: Bot, user_id: int | str) -> None:
    # Через 5 минут сообщения удалятся, если нет других новых сообщений, зависящих от декоратора delete_messages
    await asyncio.sleep(150 + 150)

    state_data: dict = await state.get_data()

    a = logging.getLogger("root")

    a.debug(f"Удаление сообщений по таймеру: {user_id=} {state_data=}")

    await messages_del(state_data, user_id, bot)

    await state.clear()

    await bot.send_message(user_id, "♻️ Превышено время ожидания, действие отменено!", disable_notification=True)


async def get_user_data(**kwargs) -> tuple[FSMContext, dict, int | str, Bot]:
    state: FSMContext = kwargs["state"]
    state_data: dict = await state.get_data()

    user: User = kwargs["event_from_user"]

    bot: Bot = kwargs["bot"]

    return state, state_data, user.id, bot


async def timer_del(state_data: dict) -> None:
    if "timer" in state_data:
        old_timer: Task = state_data["timer"]
        old_timer.cancel()


async def timer_set(state: FSMContext, bot: Bot, user_id: int | str) -> None:
    async with TaskGroup() as tg:
        new_timer: Task = tg.create_task(delete_messages_after_long_time(state, bot, user_id))
        await state.update_data(timer=new_timer)


async def messages_del(state_data: dict, user_id: int | str, bot: Bot) -> None:
    if "del_msg" in state_data:
        # state_data["del_msg"]: list[Message]
        messages_ids: list[int] = list(map(lambda x: x.message_id, state_data["del_msg"]))
        await bot.delete_messages(user_id, messages_ids)


def get_new_kwargs(func: callable, kwargs: dict) -> dict:
    func_args = inspect.getfullargspec(func).args
    new_kwargs = {key: value for (key, value) in kwargs.items() if key in func_args}
    return new_kwargs
