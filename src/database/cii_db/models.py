import datetime
from typing import Annotated

from sqlalchemy import BigInteger, ForeignKey, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.cii_db.database import Base

__all__ = [
    'TagsModel',
    'PicturesModel',
    'PictureToTagsModel',
]

int_pk = Annotated[
    int,
    mapped_column(
        primary_key=True
    )
]
bigint_pk = Annotated[
    int,
    mapped_column(
        BigInteger,
        primary_key=True
    )
]
template_created_at = Annotated[
    datetime.datetime,
    mapped_column(
        server_default=text("TIMEZONE('utc', now())")
    )
]
template_updated_at = Annotated[
    datetime.datetime,
    mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=datetime.datetime.utcnow
    )
]


class TagsModel(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        comment="Идентификатор тега"
    )
    name: Mapped[str] = mapped_column(
        comment="Название тега"
    )

    __table_args__ = (
        {'comment': 'Таблица тегов, которые могут быть связаны с изображениями'},
    )


class PicturesModel(Base):
    __tablename__ = "pictures"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        comment="Идентификатор изображения"
    )
    resolution_width: Mapped[int] = mapped_column(
        comment="Ширина разрешения изображения"
    )
    resolution_height: Mapped[int] = mapped_column(
        comment="Высота разрешения изображения"
    )
    url_page: Mapped[str] = mapped_column(
        Text,
        comment="URL страницы с изображением"
    )
    url_image: Mapped[str] = mapped_column(
        Text,
        comment="URL самого изображения"
    )
    path: Mapped[str] = mapped_column(
        Text,
        comment="Путь к изображению на сервере"
    )

    updated_at: Mapped[template_updated_at]
    created_at: Mapped[template_created_at]

    __table_args__ = (
        # UniqueConstraint('url_page', name='unique_pictures_url_page'),
        UniqueConstraint('url_image', name='unique_pictures_url_image'),
        {'comment': 'Таблица изображений с разрешениями и ссылками'},
    )


class PictureToTagsModel(Base):
    __tablename__ = "picture_to_tags"
    id: Mapped[bigint_pk]
    id_tag: Mapped[int] = mapped_column(
        ForeignKey(
            "tags.id",
            ondelete="CASCADE",
            onupdate="CASCADE"),
        comment="Идентификатор тега"
    )
    id_picture: Mapped[int] = mapped_column(
        ForeignKey(
            "pictures.id",
            ondelete="CASCADE",
            onupdate="CASCADE"
        ),
        comment="Идентификатор изображения"
    )

    __table_args__ = (
        UniqueConstraint('id_tag', 'id_picture', name='unique_picture_to_tags_id_tag_id_picture'),
        {'comment': 'Таблица связи между изображениями и тегами (многие ко многим)'},
    )
