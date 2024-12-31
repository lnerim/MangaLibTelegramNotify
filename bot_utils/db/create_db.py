from asyncio import run

from sqlalchemy.ext.asyncio import create_async_engine

from db_init import Base


async def main():
    print("Создание БД...")
    engine = create_async_engine("sqlite+aiosqlite:///../../db.sqlite", echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("БД создана")


if __name__ == '__main__':
    answer = input("Создать БД? y/n: ")
    if answer != "y":
        exit(0)
    run(main())
