from src.database.base_DAO import BaseDAO
from src.database.cii_db.models import PictureToTagsModel
from src.database.cii_db.schemas import (PictureToTagsCreateSchema,
                                         PictureToTagsUpdateSchema)

__all__ = ['PictureToTagsQuery']


class PictureToTagsQuery(BaseDAO[PictureToTagsModel, PictureToTagsCreateSchema, PictureToTagsUpdateSchema]):
    model = PictureToTagsModel
