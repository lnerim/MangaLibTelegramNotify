import inspect
import logging

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ErrorEvent


def delete_messages(func):
    async def wrapper(*args, **kwargs):
        arg = args[0]

        if isinstance(arg, ErrorEvent):
            user_id = arg.update.message.from_user.id
        else:  # Message, CallbackQuery
            user_id = arg.from_user.id

        state: FSMContext = kwargs["state"]
        bot = kwargs["bot"]

        messages = await state.get_data()
        if "del_msg" in messages:
            for m in messages["del_msg"]:
                try:
                    await bot.delete_message(user_id, m.message_id)
                except Exception as e:
                    logging.info(e)

        to_delete: list[Message] = []
        kwargs["to_delete"] = to_delete

        new_kwargs = dict()
        func_args = inspect.getfullargspec(func).args
        for i in kwargs.keys():
            if i in func_args:
                new_kwargs[i] = kwargs[i]

        await func(*args, **new_kwargs)

        if to_delete:
            await state.update_data(del_msg=to_delete)

    return wrapper
