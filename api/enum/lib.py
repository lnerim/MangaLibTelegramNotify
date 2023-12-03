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
    "1", "https://test-front.mangalib.me/", "MangaLib",
    "https://api.lib.social/api/", "https://api.lib.social/api/latest-updates",
    "https://api.lib.social/api/manga?&site_id[]=1&q="
)
RanobeLib = Lib(
    "3", "https://test-front.ranobelib.me/", "RanobeLib",
    "https://api.lib.social/api/", "https://api.lib.social/api/latest-updates",
    "https://api.lib.social/api/manga?&site_id[]=3&q="
)

SITES: dict[str, Lib] = {"1": MangaLib, "3": RanobeLib}
