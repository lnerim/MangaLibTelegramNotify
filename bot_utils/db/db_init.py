from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class DBMedia(Base):
    __tablename__ = "media"

    media_id = Column(Integer, primary_key=True)  # ID произведения

    media_type = Column(String, nullable=False)

    # Для манги и ранобэ
    last_read_chapter = Column(Float, nullable=True)
    last_read_volume = Column(Float, nullable=True)

    # Для аниме
    last_read_season = Column(Float, nullable=True)
    last_read_episode = Column(Float, nullable=True)


class DBUpdates(Base):
    __tablename__ = "updates"

    update_id = Column(Integer, primary_key=True)

    user_id = Column(Integer, nullable=False)  # ID пользователя telegram

    media_id = Column(Integer, ForeignKey(DBMedia.media_id))  # ID произведения
    site_id = Column(Integer, nullable=False)  # ID сайта
    media_name = Column(String, nullable=False)  # Название произведения