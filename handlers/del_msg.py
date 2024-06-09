import asyncio
import inspect
from asyncio import TaskGroup, Task

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ErrorEvent, CallbackQuery


def delete_messages(func) -> callable:
    async def wrapper(*args, **kwargs) -> None:
        state: FSMContext = kwargs["state"]
        state_data: dict = await state.get_data()

        if "timer" in state_data:
            old_timer: Task = state_data["timer"]
            old_timer.cancel()

        arg = args[0]

        match arg:
            case ErrorEvent():
                user_id = arg.update.message.from_user.id
            case Message() | CallbackQuery():
                user_id = arg.from_user.id
            case _:
                raise NotImplementedError(f"{type(arg)=} is not support in delete_messages")

        bot: Bot = kwargs["bot"]

        if "del_msg" in state_data:
            # state_data["del_msg"]: list[Message]
            messages_ids: list[int] = list(map(lambda x: x.message_id, state_data["del_msg"]))
            await bot.delete_messages(user_id, messages_ids)

        to_delete: list[Message] = []
        kwargs["to_delete"] = to_delete

        func_args = inspect.getfullargspec(func).args
        new_kwargs = {key: value for (key, value) in kwargs.items() if key in func_args}

        await func(*args, **new_kwargs)

        if to_delete:
            await state.update_data(del_msg=to_delete)

        async with TaskGroup() as tg:
            new_timer: Task = tg.create_task(delete_messages_after_long_time(state, bot, user_id))
            await state.update_data(timer=new_timer)

    return wrapper


async def delete_messages_after_long_time(state: FSMContext, bot: Bot, user_id: int | str):
    # Через 5 минут сообщения удалятся, если нет других новых сообщений, зависящих от декоратора delete_messages
    await asyncio.sleep(150 + 150)

    state_data: dict = await state.get_data()

    if not state_data:
        return
    # Если отменено действие и там только таймер !!! Не самое лучшее решение !!!
    elif len(state_data) == 1 and "timer" in state_data:
        return

    if "del_msg" in state_data:
        messages_ids: list[int] = list(map(lambda x: x.message_id, state_data["del_msg"]))
        await bot.delete_messages(user_id, messages_ids)

    await state.clear()

    await bot.send_message(user_id, "♻️ Превышено время ожидания, действие отменено!", disable_notification=True)
