from src.database.base_DAO import BaseDAO
from src.database.cii_db.models import TagsModel
from src.database.cii_db.schemas import (
    TagsCreateSchema, TagsUpdateSchema)

__all__ = ['TagsQuery']


class TagsQuery(
    BaseDAO[TagsModel, TagsCreateSchema, TagsUpdateSchema]
):
    model = TagsModel
