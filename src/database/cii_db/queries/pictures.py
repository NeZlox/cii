from typing import Dict, List

from pydantic import BaseModel
from sqlalchemy import select
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
