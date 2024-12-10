import logging
from dataclasses import dataclass
from datetime import datetime, date

from .media_item import MediaItem


@dataclass
class Title:
    title_id: int
    site: str
    name: str
    rus_name: str
    eng_name: str
    slug: str
    slug_url: str
    model: str
    picture: str
    last_item_at: date

    latest_items: tuple

    def __init__(self, data: dict):
        logging.debug(f"TitleInfo: {data=}")

        self.title_id = data["id"]
        self.site = data["site"]
        self.name = data["name"]
        self.rus_name = data["rus_name"]
        self.eng_name = data["eng_name"]
        self.slug = data["slug"]
        self.slug_url = data["slug_url"]
        self.model = data["model"]
        self.picture = data["cover"]["default"]
        self.last_item_at = datetime.fromisoformat(data["last_item_at"])

        self._set_latest_items(data)

    def _set_latest_items(self, data: dict):
        items = data["metadata"]["latest_items"]["items"]

        self.latest_items = tuple(map(MediaItem, items))

    @property
    def url(self):
        """example: ru/manga/206--one-piece"""
        return "ru/" + self.model + "/" + self.slug_url

    @property
    def info(self):
        """example: manga/206--one-piece"""
        return self.model + "/" + self.slug_url
