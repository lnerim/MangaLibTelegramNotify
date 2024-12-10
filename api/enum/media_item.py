import logging
from dataclasses import dataclass
from datetime import datetime


@dataclass
class MediaItem:
    item_id: int

    name: str | None
    model: str

    # Общие имена для всех сайтов
    # MangaLib, RanobeLib -> volume, number
    # AnimeLib -> season, number
    major: float
    minor: float

    created_at: datetime

    def __init__(self, data: dict):
        logging.debug(f"MediaItem: {data=}")

        self.item_id = data["id"]
        self.model = data["model"]
        self.created_at = datetime.fromisoformat(data["created_at"])

        self.name = data["name"] or None

        match self.model:
            case "chapter":
                self.major = float(data["volume"])
                self.minor = float(data["number"])
            case "episodes":
                self.major = float(data["season"])
                self.minor = float(data["number"])
            case _:
                logging.error(f"MediaItem: {data=}")
                raise Exception(f"Неизвестная модель: '{self.model}'")
