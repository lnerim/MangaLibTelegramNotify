import sqlalchemy
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# TODO Надо идентификатор произведения, потом идентификатор сайта
#  (так как на анимелиб другие идентификаторы, хотя на мангалибе и ранобэлибе они вроде одинаковые).
#  Пусть они будут ключами. Далее имя пусть тоже будет в медии, так как это логично,
#  а ключи пусть будут и обновлениях, чтобы точно обращаться к нужному. Причём в обновлениях должны
#  быть уникальными пользователь и эти ключи из другого столбца.
#  Остаётся вопрос, как удалять обновления, хотя может просто поставить флаг. Media я бы вообще не удалял

# TODO: Удалить потом
# https://github.com/kvesteri/sqlalchemy-utils/blob/baf53c/sqlalchemy_utils/models.py#L47
def _my_repr(self):
    state = sqlalchemy.inspect(self)
    field_reprs = []
    fields = state.mapper.columns.keys()
    for key in fields:
        value = state.attrs[key].loaded_value
        if key in state.unloaded:
            value = "N/A"
        else:
            value = repr(value)
        field_reprs.append('='.join((key, value)))

    return '{}({})'.format(self.__class__.__name__, ', '.join(field_reprs))

Base.__repr__ = _my_repr


class DBMedia(Base):
    __tablename__ = "media"

    media_id = Column(Integer, primary_key=True)  # ID произведения
    site_id = Column(Integer, primary_key=True)  # ID сайта

    media_name = Column(String, nullable=False)

    # Для манги и ранобэ
    last_read_chapter = Column(Float, nullable=False, default=0.0)
    last_read_volume = Column(Float, nullable=False, default=0.0)

    # Для аниме
    last_read_season = Column(Float, nullable=False, default=0.0)
    last_read_episode = Column(Float, nullable=False, default=0.0)


class DBUpdates(Base):
    __tablename__ = "updates"

    user_id = Column(Integer, primary_key=True)  # ID пользователя telegram

    media_id = Column(Integer, ForeignKey(DBMedia.media_id), primary_key=True)  # ID произведения
    site_id = Column(Integer, ForeignKey(DBMedia.site_id), primary_key=True)  # ID сайта

    update_enabled = Column(Boolean, nullable=False, default=1)
