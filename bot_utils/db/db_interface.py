from sqlalchemy import update, select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.util import generic_repr

from db_init import DBMedia, DBUpdates
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

    # FIXME: Возможно изменились входные данные
    async def publication_add(self, user_id: int, media_id: int, site_id: int, name: str) -> None:
        stmt_media = insert(DBMedia).values(
            media_id=media_id, site_id=site_id,
            media_name=name
        ).on_conflict_do_nothing()

        stmt_upd = insert(DBUpdates).values(
            user_id=user_id, media_id=media_id, site_id=site_id
        ).on_conflict_do_update(
            index_elements=[DBUpdates.user_id, DBUpdates.media_id, DBUpdates.site_id],
            set_=dict(update_enabled=True)
        )

        async with self.async_session() as session:
            await session.execute(stmt_media)
            await session.commit()
            await session.execute(stmt_upd)
            await session.commit()

    # FIXME: Возможно изменились входные данные
    async def publication_delete(self, user_id: int, media_id: int, site_id: int) -> None:
        stmt = update(DBUpdates).where(
            user_id == DBUpdates.user_id, media_id == DBUpdates.media_id, site_id == DBUpdates.site_id
        ).values(update_enabled=False)

        async with self.async_session() as session:
            await session.execute(stmt)
            await session.commit()

    # FIXME: Возможно изменились входные данные
    async def users_by_publication(self, media_id: int, site_id: int) -> list[DBUpdates]:
        stmt = select(DBUpdates).where(
            media_id == DBUpdates.media_id, site_id == DBUpdates.site_id,
            True == DBUpdates.update_enabled
        )
        async with self.async_session() as session:
            result = await session.execute(stmt)
            return list(result.scalars().all())

    # FIXME: Возможно изменились входные данные
    async def publications_by_user(self, user_id: int) -> list[DBUpdates]:
        stmt = select(DBUpdates).where(
            user_id == DBUpdates.user_id, True == DBUpdates.update_enabled
        )
        async with self.async_session() as session:
            result = await session.execute(stmt)
            return list(result.scalars().all())

    # FIXME: Возможно изменились входные данные
    async def publication_get(self, media_id: int, site_id: int) -> DBMedia | None:
        stmt = select(DBMedia).where(
            media_id == DBMedia.media_id, site_id == DBMedia.site_id
        )
        async with self.async_session() as session:
            result = await session.execute(stmt)
            return result.scalars().first()


db_new = DBInterface("db.sqlite")

async def main():
    # print(generic_repr(await db_new.publication_add(1158, 1156, 52, "test")))
    print(generic_repr(await db_new.publication_delete(1158, 1156, 52)))
    result = await db_new.users_by_publication(1156, 52)
    print(result)
    print(len(result))
    print()


if __name__ == "__main__":
    asyncio.run(main())
