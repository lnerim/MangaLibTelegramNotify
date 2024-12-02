from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.util import generic_repr

from db_init import DBMedia
import asyncio


class DBInterface:
    def __init__(self, name_db: str = "db.sqlite"):
        self.engine = create_async_engine(f"sqlite+aiosqlite:///{name_db}", echo=True)
        self.async_session = async_sessionmaker(bind=self.engine, expire_on_commit=False)

    async def check_publication_in_db(self, publication_ids: list[int]) -> list[int]:
        stmt = select(DBMedia.media_id).where(DBMedia.media_id.in_(publication_ids))
        async with self.async_session() as session:
            result = await session.execute(stmt)
            existing_ids = result.scalars().all()
            return list(existing_ids)

    async def publication_add(self, title_id: int, user_id: int, site_id: int, name: str) -> None:
        raise NotImplementedError()

    async def publication_delete(self, key: int) -> None:
        raise NotImplementedError()

    async def users_by_publication(self, title_id: int) -> list[tuple[int, int]] | None:
        raise NotImplementedError()

    async def publications_by_user(self, user_id: int) -> list | None:
        raise NotImplementedError()

    async def publication_name_by_key(self, key: int) -> str:
        stmt = select(DBMedia).where(key == DBMedia.media_id)
        async with self.async_session() as session:
            result = await session.execute(stmt)
            return result.scalars().first()


db_new = DBInterface("test_db.sqlite")

async def main():
    print(generic_repr(await db_new.check_publication_in_db([1, 2, 3])))
    print(generic_repr(await db_new.publication_name_by_key(1)))
    print()


if __name__ == "__main__":
    asyncio.run(main())
