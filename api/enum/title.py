import logging
from dataclasses import dataclass
from datetime import datetime

from .media_item import MediaItem


@dataclass
class Title:
    title_id: int
    site: str
    site_id: int
    name: str
    rus_name: str
    eng_name: str
    slug: str
    slug_url: str
    model: str
    picture: str
    last_item_at: datetime

    latest_items: tuple[MediaItem, ...]

    @staticmethod
    def from_json(data: dict, latest_updates: datetime) -> "Title":
        logging.debug(f"TitleInfo: {data=}")

        title_id = data["id"]
        site = data["site"]
        site_id = int(data["site"])
        name = data["name"]
        rus_name = data["rus_name"]
        eng_name = data["eng_name"]
        slug = data["slug"]
        slug_url = data["slug_url"]
        model = data["model"]
        picture = data["cover"]["default"]
        last_item_at = datetime.fromisoformat(data["last_item_at"])

        items = data["metadata"]["latest_items"]["items"]

        latest_items: tuple[MediaItem, ...] = tuple(map(MediaItem.from_json, items))
        latest_items = tuple(
            filter(
                lambda x: x.created_at > latest_updates,
                latest_items
            )
        )

        # FIXME
        if not latest_items:
            logging.warning(f"===Пустой Title===")
            logging.warning(f"{data=}")
            logging.warning(f"{latest_updates=}")
            logging.warning(f"{latest_items=}")

        return Title(title_id, site, site_id, name, rus_name, eng_name, slug,
                     slug_url, model, picture, last_item_at, latest_items)

    @property
    def url(self):
        """example: ru/manga/206--one-piece"""
        return "ru/" + self.model + "/" + self.slug_url

    @property
    def info(self):
        """example: manga/206--one-piece"""
        return self.model + "/" + self.slug_url
