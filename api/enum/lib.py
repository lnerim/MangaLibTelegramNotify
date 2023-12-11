from dataclasses import dataclass


@dataclass
class Lib:
    site_id: str
    url: str
    name: str
    api: str
    latest_updates: str
    search: str


MangaLib = Lib(
    site_id="1",
    url="https://test-front.mangalib.me/",
    name="MangaLib",
    api="https://api.lib.social/api/",
    latest_updates="https://api.lib.social/api/latest-updates",
    search="https://api.lib.social/api/manga?&site_id[]=1&q="
)
RanobeLib = Lib(
    site_id="3",
    url="https://test-front.ranobelib.me/",
    name="RanobeLib",
    api="https://api.lib.social/api/",
    latest_updates="https://api.lib.social/api/latest-updates",
    search="https://api.lib.social/api/manga?&site_id[]=3&q="
)
AnimeLib = Lib(
    site_id="5",
    url="https://test-front.animelib.me/",
    name="AnimeLib",
    api="https://api.lib.social/api/",
    latest_updates="https://api.lib.social/api/latest-updates",
    search="https://api.lib.social/api/anime?&site_id[]=5&q="
)

SITES: dict[str, Lib] = {"1": MangaLib, "3": RanobeLib, "5": AnimeLib}
