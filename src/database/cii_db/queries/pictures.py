from typing import Dict, List

from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError

from src.database.base_DAO import BaseDAO
from src.database.cii_db.models import (PicturesModel, PictureToTagsModel,
                                        TagsModel)
from src.database.cii_db.schemas import (PicturesCreateSchema,
                                         PicturesUpdateSchema)

__all__ = ['PicturesQuery']

from src.exceptions import CannotExecuteQueryToDatabase
from src.logger import logger


class PicturesWithTagsSchema(BaseModel):
    pass


class PicturesQuery(
    BaseDAO[PicturesModel, PicturesCreateSchema, PicturesUpdateSchema]
):
    model = PicturesModel

    @classmethod
    async def get_pictures_with_tags(cls, cnt: int = 10, start: int = 0) -> List[Dict[str, str]]:
        async with cls.async_session_maker() as session:
            try:
                # Запрос для получения изображений с тегами
                query = (
                    select(cls.model.id, cls.model.path, TagsModel.name)
                    .join(PictureToTagsModel, cls.model.id == PictureToTagsModel.id_picture)
                    .join(TagsModel, PictureToTagsModel.id_tag == TagsModel.id)
                    .order_by(cls.model.id)
                    .offset(start)
                    .limit(cnt)
                )
                result_orm = await session.execute(query)
                result = result_orm.mappings().all()

                if result:
                    return result
                else:
                    return []

            except (SQLAlchemyError, Exception) as e:
                await session.rollback()
                if isinstance(e, SQLAlchemyError):
                    msg = "PicturesQuery Database error"
                else:
                    msg = "PicturesQuery Unknown error"

                msg += ": Cannot get_pictures_with_tags"

                extra = {
                    "error": e,
                    "query": cnt
                }

                logger.error(msg, extra=extra, exc_info=True)
                raise CannotExecuteQueryToDatabase

    @classmethod
    async def get_pictures_with_tags_by_ids(cls, image_ids: List[int]) -> List[Dict[str, str]]:
        async with cls.async_session_maker() as session:
            try:
                # Запрос для получения изображений по списку идентификаторов
                query = (
                    select(
                        PicturesModel.id.label('id'),
                        PicturesModel.resolution_width.label('resolution_width'),
                        PicturesModel.resolution_height.label('resolution_height'),
                        PicturesModel.url_page.label('url_page'),
                        PicturesModel.url_image.label('url_image'),
                        PicturesModel.path.label('path'),
                        func.array_agg(
                            func.jsonb_build_object('id', TagsModel.id, 'name', TagsModel.name)
                        ).label('tags')  # Аггрегируем теги в массив
                    )
                    .join(PictureToTagsModel, PictureToTagsModel.id_picture == PicturesModel.id)
                    .join(TagsModel, TagsModel.id == PictureToTagsModel.id_tag)
                    .filter(PicturesModel.id.in_(image_ids))
                    .group_by(
                        PicturesModel.id.label('id'),
                        PicturesModel.resolution_width.label('resolution_width'),
                        PicturesModel.resolution_height.label('resolution_height'),
                        PicturesModel.url_page.label('url_page'),
                        PicturesModel.url_image.label('url_image'),
                        PicturesModel.path.label('path'),
                    )
                )

                result_orm = await session.execute(query)
                result = result_orm.mappings().all()

                return result
            except (SQLAlchemyError, Exception) as e:
                await session.rollback()
                if isinstance(e, SQLAlchemyError):
                    msg = "PicturesQuery Database error"
                else:
                    msg = "PicturesQuery Unknown error"

                msg += ": Cannot get_pictures_with_tags_by_ids"

                extra = {
                    "error": e,
                    "image_ids": image_ids
                }

                logger.error(msg, extra=extra, exc_info=True)
                raise CannotExecuteQueryToDatabase
