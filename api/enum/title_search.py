import logging
from dataclasses import dataclass


@dataclass
class TitleSearch:
    title_id: int
    site: str
    site_id: int
    name: str
    rus_name: str
    eng_name: str
    slug: str
    slug_url: str
    picture: str


    @staticmethod
    def from_json(data: dict) -> "TitleSearch":
        logging.debug(f"TitleSearch: {data=}")

        title_id = data["id"]
        site = data["site"]
        site_id = int(data["site"])
        name = data["name"]
        rus_name = data["rus_name"]
        eng_name = data["eng_name"]
        slug = data["slug"]
        slug_url = data["slug_url"]
        picture = data["cover"]["default"]


        return TitleSearch(title_id, site, site_id, name, rus_name,
                           eng_name, slug, slug_url, picture)
