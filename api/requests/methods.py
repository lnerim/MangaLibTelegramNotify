import json

from httpx import AsyncClient, Response

from api.enum import Title
from api.enum.lib import Lib, SITES


async def _get_from_api(site: Lib, url: str) -> dict:
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

    return json.loads(data.content)["data"]


async def get_latest_updates(site: Lib) -> tuple[Title, ...]:
    updates = await _get_from_api(site, site.latest_updates)
    titles: tuple[Title, ...] = tuple(map(Title, updates))
    return titles


async def search(site_id: str, name: str) -> tuple[Title, ...]:
    site: Lib = SITES[site_id]
    data = await _get_from_api(site, site.search + name)
    titles: tuple[Title, ...] = tuple(map(Title, data))
    return titles
