from dataclasses import dataclass


@dataclass
class Lib:
    site_id: str
    url: str
    name: str
    api: str
    model: str
    latest_updates: str
    search: str
    info: str


MangaLib = Lib(
    site_id="1",
    url="https://mangalib.me/",
    name="MangaLib",
    api="https://api2.mangalib.me/api/",
    model="manga",
    latest_updates="https://api2.mangalib.me/api/latest-updates",
    search="https://api2.mangalib.me/api/manga?&site_id[]=1&q=",
    info="?fields[]=eng_name&fields[]=summary&fields[]=releaseDate&fields[]=type_id&fields[]=caution&fields[]=views&"
         "fields[]=rate_avg&fields[]=rate&fields[]=genres&fields[]=tags&fields[]=authors&fields[]=userRating&"
         "fields[]=manga_status_id&fields[]=status_id"
)
RanobeLib = Lib(
    site_id="3",
    url="https://ranobelib.me/",
    name="RanobeLib",
    api="https://api2.mangalib.me/api/",
    model="manga",
    latest_updates="https://api2.mangalib.me/api/latest-updates",
    search="https://api2.mangalib.me/api/manga?&site_id[]=3&q=",
    info="?fields[]=eng_name&fields[]=summary&fields[]=releaseDate&fields[]=type_id&fields[]=caution&fields[]=views&"
         "fields[]=rate_avg&fields[]=rate&fields[]=genres&fields[]=tags&fields[]=authors&fields[]=userRating&"
         "fields[]=manga_status_id&fields[]=status_id"
)
AnimeLib = Lib(
    site_id="5",
    url="https://anilib.me/",
    name="AnimeLib",
    api="https://api2.mangalib.me/api/",
    model="anime",
    latest_updates="https://api2.mangalib.me/api/latest-updates",
    search="https://api2.mangalib.me/api/anime?&site_id[]=5&q=",
    info="?fields[]=eng_name&fields[]=summary&fields[]=releaseDate&fields[]=type_id&fields[]=caution&fields[]=views&"
         "fields[]=rate_avg&fields[]=rate&fields[]=genres&fields[]=tags&fields[]=authors&fields[]=userRating&"
         "fields[]=anime_status_id"
)

SITES: dict[str, Lib] = {"1": MangaLib, "3": RanobeLib, "5": AnimeLib}
