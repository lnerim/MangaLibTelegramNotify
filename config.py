from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis


DEBUG_MODE = bool(getenv("DEBUG_MODE", default=False))

bot = Bot(token=getenv("TOKEN"))
redis = Redis.from_url(getenv("REDIS"))
storage = RedisStorage(redis)
dp = Dispatcher(storage=storage)
