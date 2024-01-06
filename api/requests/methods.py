from httpx import AsyncClient, Response

from api.enum import Title, TitleInfo
from api.enum.lib import Lib, SITES


async def _get_from_api(site: Lib, url: str):
    async with AsyncClient(http2=True) as client:
        data: Response = await client.get(
            url=url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/119.0.0.0 Safari/537.36",
                "Accept": "*/*",
                "Accept-Encoding": "utf-8",
                "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                "Content-Type": "application/json",
                "Origin": site.url,
                "Referer": site.url,
                "Site-Id": site.site_id
            }
        )
        data.raise_for_status()

    return data.json()["data"]


async def get_latest_updates(site: Lib) -> tuple[Title, ...]:
    # TODO Пусть принимает на вход время и пока не дойдёт до него, то будет слать новые запросы страниц
    #  http://api.lib.social/api/latest-updates?page=2 и так далее...
    updates = await _get_from_api(site, site.latest_updates)
    titles: tuple[Title, ...] = tuple(map(Title, updates))
    return titles


async def search(site_id: str, name: str) -> tuple[Title, ...]:
    site: Lib = SITES[site_id]
    data = await _get_from_api(site, site.search + name)
    titles: tuple[Title, ...] = tuple(map(Title, data))
    return titles


async def more_info(site_id: str, slug: str) -> TitleInfo:
    site: Lib = SITES[site_id]
    url: str = site.api + site.model + "/" + slug + site.info
    data = await _get_from_api(site, url)
    title_info = TitleInfo(data)
    return title_info
