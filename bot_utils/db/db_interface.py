from sqlalchemy import update, select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from .db_init import DBMedia, DBUpdates


class DBInterface:
    def __init__(self, name_db: str = "db.sqlite"):
        self.engine = create_async_engine(f"sqlite+aiosqlite:///{name_db}", echo=False)
        self.async_session = async_sessionmaker(bind=self.engine, expire_on_commit=False)

    async def check_publication_in_db(self, publication_ids: list[int], site_id: int) -> list[int]:
        stmt = select(DBMedia.media_id).where(
            DBMedia.media_id.in_(publication_ids), site_id == DBMedia.site_id
        )
        async with self.async_session() as session:
            result = await session.execute(stmt)
            existing_ids = result.scalars().all()
            return list(existing_ids)

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

    async def publication_delete(self, user_id: int, media_id: int, site_id: int) -> None:
        stmt = update(DBUpdates).where(
            user_id == DBUpdates.user_id, media_id == DBUpdates.media_id, site_id == DBUpdates.site_id
        ).values(update_enabled=False)

        async with self.async_session() as session:
            await session.execute(stmt)
            await session.commit()

    async def users_by_publication(self, media_id: int, site_id: int) -> list[DBUpdates]:
        stmt = select(DBUpdates).where(
            media_id == DBUpdates.media_id, site_id == DBUpdates.site_id,
            True == DBUpdates.update_enabled
        )
        async with self.async_session() as session:
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def publications_by_user(self, user_id: int) -> list[DBUpdates]:
        stmt = select(DBUpdates).where(
            user_id == DBUpdates.user_id, True == DBUpdates.update_enabled
        )
        async with self.async_session() as session:
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def publication_get(self, media_id: int, site_id: int) -> DBMedia | None:
        stmt = select(DBMedia).where(
            media_id == DBMedia.media_id, site_id == DBMedia.site_id
        )
        async with self.async_session() as session:
            result = await session.execute(stmt)
            return result.scalars().first()

    async def publication_update(self,
                                 title_id: int, site_id: int,
                                 major: float, minor: float) -> None:
        stmt = update(DBMedia).where(
            title_id == DBMedia.media_id, site_id == DBMedia.site_id
        ).values(major=major, minor=minor)

        async with self.async_session() as session:
            await session.execute(stmt)
            await session.commit()


db_new = DBInterface("db.sqlite")
