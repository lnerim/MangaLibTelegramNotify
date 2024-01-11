from aiogram.fsm.state import StatesGroup, State


class Search(StatesGroup):
    wait_site = State()
    wait_input = State()
    choose_title = State()
