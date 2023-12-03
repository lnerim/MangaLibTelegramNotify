from dataclasses import dataclass
from datetime import datetime, date


@dataclass
class Title:
    title_id: int
    site: str
    name: str
    rus_name: str
    eng_name: str
    slug: str
    model: str
    picture: str
    last_item_at: date | None = None

    def __init__(self, data: dict):
        self.title_id = data["id"]
        self.site = data["site"]
        self.name = data["name"]
        self.rus_name = data["rus_name"]
        self.eng_name = data["eng_name"]
        self.slug = data["slug"]
        self.slug_url = data["slug_url"]
        self.model = data["model"]
        self.picture = data["cover"]["thumbnail"]
        self.last_item_at = datetime.fromisoformat(data["last_item_at"]) \
            if "last_item_at" in data else None

    @property
    def url(self):
        """example: ru/manga/206--one-piece"""
        return "ru/" + self.model + "/" + self.slug_url
