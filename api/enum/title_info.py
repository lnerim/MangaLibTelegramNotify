from dataclasses import dataclass

from api.enum import Title


@dataclass
class TitleInfo(Title):
    ageRestriction: str = ""
    authors: tuple[str, ...] = tuple()
    genres: tuple[str, ...] = tuple()
    rating: str = ""
    releaseDateString: str = ""
    status: str = ""
    summary: str = ""
    tags: tuple[str, ...] = tuple()
    type: str = ""

    def __init__(self, data: dict):
        super().__init__(data)

        self.ageRestriction = data["ageRestriction"]["label"]
        self.authors = tuple(map(lambda x: x["name"], data["authors"]))
        self.genres = tuple(map(lambda x: x["name"], data["genres"]))
        self.rating = data["rating"]["average"]
        self.releaseDateString = data["releaseDateString"]
        self.status = data["status"]["label"]
        self.summary = data["summary"] or "Описание отсутствует"
        self.tags = tuple(map(lambda x: x["name"], data["tags"]))
        self.type = data["type"]["label"]
