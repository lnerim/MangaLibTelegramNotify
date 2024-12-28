from asyncio import sleep
from datetime import datetime
import logging

from httpx import AsyncClient, Response

from api.enum import Title, TitleInfo
from api.enum.lib import Lib, SITES
from api.enum.title_search import TitleSearch
from bot_utils import db_new


async def _get_from_api(site: Lib, url: str):
    async with AsyncClient(http2=True) as client:
        data: Response = await client.get(
            url=url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/131.0.0.0 Safari/537.36",
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


async def get_latest_updates(site: Lib, last_update: datetime) -> tuple[datetime, tuple[Title, ...]]:
    updates: list[dict, ...] = await _get_from_api(site, site.latest_updates)

    page = 2
    while datetime.fromisoformat(updates[-1]["last_item_at"]) > last_update:
        await sleep(0.5)
        updates += await _get_from_api(site, site.latest_updates + f"?page={page}")
        page += 1
        logging.info(f"{datetime.fromisoformat(updates[-1]["last_item_at"])} {last_update}")
        if page >= 5:
            logging.error("===Превышение===")
            logging.error(f"{site.name} {last_update} {datetime.fromisoformat(updates[-1]['last_item_at'])}")
            break

    updates_ids = [int(t["id"]) for t in updates]
    updates_ids = await db_new.check_publication_in_db(updates_ids, int(site.site_id))

    titles = list()
    for t in updates:
        if int(t["id"]) in updates_ids:
            titles.append(
                Title.from_json(t, last_update)
            )

    filtered_titles: tuple[Title, ...] = tuple(filter(lambda t: t.last_item_at > last_update, titles))
    new_update: datetime = datetime.fromisoformat(updates[0]["last_item_at"])

    return new_update, filtered_titles


async def search(site_id: str, name: str) -> tuple[TitleSearch, ...]:
    site: Lib = SITES[site_id]
    data = await _get_from_api(site, site.search + name)
    titles: tuple[TitleSearch, ...] = tuple(map(TitleSearch.from_json, data))
    return titles


async def more_info(site_id: str, slug: str) -> TitleInfo:
    site: Lib = SITES[site_id]
    url: str = site.api + site.model + "/" + slug + site.info
    data = await _get_from_api(site, url)
    title_info = TitleInfo(data)
    return title_info
