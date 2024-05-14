import inspect

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ErrorEvent, CallbackQuery


def delete_messages(func) -> callable:
    async def wrapper(*args, **kwargs) -> None:
        arg = args[0]

        match arg:
            case ErrorEvent():
                user_id = arg.update.message.from_user.id
            case Message() | CallbackQuery():
                user_id = arg.from_user.id
            case _:
                raise NotImplementedError(f"{type(arg)=} is not support in delete_messages")

        state: FSMContext = kwargs["state"]
        bot: Bot = kwargs["bot"]

        messages: dict = await state.get_data()
        if "del_msg" in messages:
            # messages["del_msg"]: list[Message]
            messages_ids: list[int] = list(map(lambda x: x.message_id, messages["del_msg"]))
            await bot.delete_messages(user_id, messages_ids)

        to_delete: list[Message] = []
        kwargs["to_delete"] = to_delete

        func_args = inspect.getfullargspec(func).args
        new_kwargs = {key: value for (key, value) in kwargs.items() if key in func_args}

        await func(*args, **new_kwargs)

        if to_delete:
            await state.update_data(del_msg=to_delete)

    return wrapper
