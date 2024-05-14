from aiogram.filters.callback_data import CallbackData


class TitleData(CallbackData, prefix="title"):
    title_id: int | str
    site_id: int | str


class ItemData(CallbackData, prefix="item"):
    key: int | str
    page: int


class ItemDataDelete(CallbackData, prefix="delete"):
    key: int | str
    page: int
    delete: bool


class NavigationData(CallbackData, prefix="nav"):
    page: int


class SearchTitle(CallbackData, prefix="search"):
    site_id: int | str
