import asyncio
import logging
import time
import traceback

import httpx

from config import redis


async def update_proxy_task(*, url_proxy: str, url_check: str):
    while True:
        try:
            logging.info("Обновление прокси")
            await set_proxy(url_proxy=url_proxy, url_check=url_check)

        except Exception as e:
            logging.error(f"update_proxy_task error: {e}\n{traceback.format_exc()}")

        finally:
            await asyncio.sleep(int(60 * 60))  # Час


async def set_proxy(*, url_proxy: str, url_check: str):
    proxy_list = await check_all_proxy(url_proxy, url_check)

    async with redis.pipeline() as pipe:
        await pipe.delete("proxies")

        for proxy_data in proxy_list:
            if proxy_data["ok"]:
                await pipe.zadd("proxies", {proxy_data["proxy"]: proxy_data["delay"]})

        await pipe.execute()


async def check_all_proxy(url_proxy: str, url_check: str):
    proxy_list = await get_proxy_list(url_proxy)

    tasks = [check_proxy(proxy=proxy, url=url_check) for proxy in proxy_list]

    # Результаты приходят по мере выполнения
    result_proxy = []
    for coro in asyncio.as_completed(tasks):
        result = await coro
        result_proxy.append(result)
        logging.info(f"Прокси проверена {result=}")

    return result_proxy


async def get_proxy_list(url):
    # Типа всегда доступен, ошибки отсюда будут только где-то выше обрабатываться
    async with httpx.AsyncClient() as client:
        r = await client.get(url)

    proxy_list = r.text.split("\n")

    return proxy_list


async def check_proxy(*, proxy: str, url: str):
    async def _do():
        async with httpx.AsyncClient(proxy=proxy, timeout=15.0) as client:
            return await client.get(url)

    try:
        t0 = time.perf_counter()
        r = await asyncio.wait_for(_do(), timeout=15.0)
        dt = time.perf_counter() - t0
        return {"proxy": proxy, "ok": True, "delay": dt, "response": r}

    except Exception as e:
        return {"proxy": proxy, "ok": False, "msg": f"{type(e)} {e}"}

