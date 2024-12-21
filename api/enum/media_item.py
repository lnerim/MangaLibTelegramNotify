import logging
from dataclasses import dataclass
from datetime import datetime

from bot_utils.db import DBMedia


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

    @staticmethod
    def from_json(data: dict) -> "MediaItem":
        logging.debug(f"MediaItem: {data=}")

        item_id = data["id"]
        model = data["model"]

        name = data["name"] or None

        match model:
            case "chapter":
                major = float(data["volume"])
                minor = float(data["number"])
                created_at = datetime.fromisoformat(data["created_at"])
            case "episodes":
                major = float(data["season"])
                minor = float(data["number"])
                created_at = datetime.fromisoformat(data["created_at"])
                for player in data["players"]:
                    created_at = max(created_at, datetime.fromisoformat(player["created_at"]))
            case _:
                logging.error(f"MediaItem: {data=}")
                raise Exception(f"Неизвестная модель: '{model}'")

        return MediaItem(item_id, name, model, major, minor, created_at)

    @property
    def get_str(self):
        major = int(self.major) if self.major.is_integer() else self.major
        minor = int(self.minor) if self.minor.is_integer() else self.minor

        match self.model:
            case "chapter":
                result_str = f"Том {major} Глава {minor}"
            case "episodes":
                result_str = f"Сезон {major} Серия {minor}"
            case _:
                logging.error(f"MediaItem: {self.model=}")
                raise Exception(f"Неизвестная модель: '{self.model}'")

        if self.name:
            result_str += f"\n{self.name}\n"

        return result_str

    def __mod__(self, other: DBMedia) -> bool:
        # TODO Проверить корректность, либо протестировать
        #  Да и mod поменять стоит, скорее всего
        if not isinstance(other, DBMedia):
            raise TypeError(f"DBMedia expected, got {type(other)} instead")

        # True - со звуком
        # False - без звука
        # other - значение из БД
        if other.major > self.major:
            return False
        elif other.major < self.major:
            return True
        elif other.minor >= self.minor:
            return False

        return True
