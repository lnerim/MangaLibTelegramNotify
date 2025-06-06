from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class DBMedia(Base):
    __tablename__ = "media"

    media_id = Column(Integer, primary_key=True)  # ID произведения
    site_id = Column(Integer, primary_key=True)  # ID сайта

    media_name = Column(String, nullable=False)

    major = Column(Float, nullable=False, default=0.0)
    minor = Column(Float, nullable=False, default=0.0)


class DBUpdates(Base):
    __tablename__ = "updates"

    user_id = Column(Integer, primary_key=True)  # ID пользователя telegram

    media_id = Column(Integer, ForeignKey(DBMedia.media_id), primary_key=True)  # ID произведения
    site_id = Column(Integer, ForeignKey(DBMedia.site_id), primary_key=True)  # ID сайта

    update_enabled = Column(Boolean, nullable=False, default=1)
