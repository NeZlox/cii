from typing import List

from sqlalchemy import select, insert, delete
from sqlalchemy.dialects.postgresql import insert as pg_insert
from src.database.base_DAO import BaseDAO
from src.database.cii_db.models import *
from src.logger import logger
from src.exceptions import CannotInsertDataToDatabase
from sqlalchemy.exc import SQLAlchemyError
from src.database.cii_db.schemas import PicturesCreateSchema

__all__ = ['TransactionSessionQuery']


class TransactionSessionQuery(BaseDAO):
    pass

    @classmethod
    async def insert_new_picture(cls, info_picture: PicturesCreateSchema, tags: List[str]):
        async with cls.async_session_maker() as session:
            try:

                async with session.begin():
                    # 1. Получаем теги из базы, соответствующие переданным
                    existing_tags = await session.execute(
                        select(TagsModel).where(TagsModel.name.in_(tags))
                    )
                    existing_tags = {tag.name: tag for tag in existing_tags.scalars()}

                    # 2. Создаём новые теги, которых нет в базе
                    new_tags = [TagsModel(name=tag) for tag in tags if tag not in existing_tags]
                    session.add_all(new_tags)
                    await session.flush()  # Получаем id для новых тегов

                    # Обновляем словарь тегов
                    all_tags = {**existing_tags, **{tag.name: tag for tag in new_tags}}

                    # 3. Добавляем изображение или обновляем его, используя ON CONFLICT
                    picture_insert_stmt = pg_insert(PicturesModel).values(
                        resolution_width=info_picture.resolution_width,
                        resolution_height=info_picture.resolution_height,
                        url_page=str(info_picture.url_page),
                        url_image=str(info_picture.url_image),
                        path=info_picture.path
                    ).on_conflict_do_update(
                        index_elements=['url_image'],  # Конфликт по уникальному URL изображения
                        set_=dict(
                            resolution_width=info_picture.resolution_width,
                            resolution_height=info_picture.resolution_height,
                            url_page=str(info_picture.url_page),
                            path=info_picture.path
                        )
                    ).returning(PicturesModel.id)

                    picture_result = await session.execute(picture_insert_stmt)
                    picture_id = picture_result.scalar()

                    # 4. Получаем текущие связи изображения с тегами
                    existing_picture_tags = await session.execute(
                        select(PictureToTagsModel)
                        .where(PictureToTagsModel.id_picture == picture_id)
                    )
                    existing_picture_tags = {ptt.id_tag for ptt in existing_picture_tags.scalars()}

                    # 5. Определяем теги для добавления и удаления
                    new_tag_ids = {tag.id for tag in all_tags.values()}
                    tags_to_add = new_tag_ids - existing_picture_tags
                    tags_to_remove = existing_picture_tags - new_tag_ids

                    # 6. Удаляем устаревшие связи с тегами
                    if tags_to_remove:
                        await session.execute(
                            delete(PictureToTagsModel)
                            .where(PictureToTagsModel.id_picture == picture_id)
                            .where(PictureToTagsModel.id_tag.in_(tags_to_remove))
                        )

                    # 7. Добавляем новые связи между изображением и тегами
                    picture_to_tag_entries = [
                        PictureToTagsModel(id_picture=picture_id, id_tag=tag_id)
                        for tag_id in tags_to_add
                    ]
                    session.add_all(picture_to_tag_entries)

                    await session.commit()
                    return True

            except (SQLAlchemyError, Exception) as e:
                await session.rollback()
                if isinstance(e, SQLAlchemyError):

                    msg = "TransactionSessionQuery Database error"

                else:

                    msg = "TransactionSessionQuery Unknown error"

                msg += ": Cannot insert_new_picture"

                extra = {

                    "query": {'info_picture': info_picture.model_dump(mode='json'), 'tags': tags},
                    "error": e

                }

                logger.error(msg, extra=extra, exc_info=True)
                raise CannotInsertDataToDatabase
