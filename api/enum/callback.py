from aiogram.filters.callback_data import CallbackData


class TitleData(CallbackData, prefix="title"):
    title_id: int | str
    site_id: int | str


class ItemData(CallbackData, prefix="item"):
    item_id: int
    site_id: int
    page: int


class ItemDataDelete(CallbackData, prefix="delete"):
    item_id: int
    site_id: int
    page: int
    delete: bool


class NavigationData(CallbackData, prefix="nav"):
    page: int


class SearchTitle(CallbackData, prefix="search"):
    site_id: int | str
