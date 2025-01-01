import logging
from dataclasses import dataclass


@dataclass
class TitleInfo:
    title_id: int
    site: str
    name: str
    rus_name: str
    eng_name: str
    slug: str
    slug_url: str
    model: str
    picture: str

    ageRestriction: str
    authors: tuple[str, ...]
    genres: tuple[str, ...]
    rating: str
    releaseDateString: str
    status: str
    summary: str
    tags: tuple[str, ...]
    type: str

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

        self.ageRestriction = data["ageRestriction"]["label"]
        self.authors = tuple(map(lambda x: x["name"], data["authors"]))
        self.genres = tuple(map(lambda x: x["name"], data["genres"]))
        self.rating = data["rating"]["average"]
        self.releaseDateString = data["releaseDateString"]
        self.status = data["status"]["label"]
        self.summary = data["summary"] or "Описание отсутствует"
        self.tags = tuple(map(lambda x: x["name"], data["tags"]))
        self.type = data["type"]["label"]
