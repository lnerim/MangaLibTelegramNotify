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

    additional_data: str

    @staticmethod
    def from_json(data: dict) -> "MediaItem":
        logging.debug(f"MediaItem: {data=}")

        item_id = data["id"]
        model = data["model"]

        name = data["name"] or None

        additional_data = "\n\n"

        match model:
            case "chapter":
                major = float(data["volume"])
                minor = float(data["number"])
                created_at = datetime.fromisoformat(data["created_at"])
            case "episodes":
                major = float(data["season"])
                minor = float(data["number"])

                max_created_at_player = max(
                    data["players"],
                    key=lambda x: datetime.fromisoformat(x["created_at"])
                )
                created_at = datetime.fromisoformat(max_created_at_player["created_at"])

                players = sorted(
                    data["players"],
                    key=lambda x: int(x["id"]),
                    reverse=True
                )

                for n, player in enumerate(players[:5], start=1):
                    # logging.info(f"{player=}")
                    additional_data += f"{n}. "
                    additional_data += f"{player["player"]} "
                    additional_data += f"{player["translation_type"]["label"]} "
                    additional_data += f"{player["team"]["name"]}\n"
            case _:
                logging.error(f"MediaItem: {data=}")
                raise Exception(f"Неизвестная модель: '{model}'")

        return MediaItem(item_id, name, model, major, minor, created_at, additional_data)

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

        result_str += self.additional_data

        return result_str

    def __format__(self, format_spec) -> str:
        match format_spec:
            case "info":
                return self.get_str
            case _:
                return super().__format__(format_spec)

    def __mod__(self, other: DBMedia) -> bool:
        if not isinstance(other, DBMedia):
            raise TypeError(f"DBMedia expected, got {type(other)} instead")

        # True - без звука
        # False - со звуком
        # other - значение из БД
        logging.info(f"{other.major=} {other.minor=}, {self.major=} {self.minor=}")
        if other.major > self.major:
            logging.info(f"{other.major > self.major=}")
            return True
        elif other.major < self.major:
            logging.info(f"{other.major < self.major=}")
            return False
        elif other.minor >= self.minor:
            logging.info(f"{other.major >= self.major=}")
            return True

        logging.info(f"{False}")
        return False
