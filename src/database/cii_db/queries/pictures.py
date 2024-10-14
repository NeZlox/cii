from src.database.base_DAO import BaseDAO
from src.database.cii_db.models import PicturesModel
from src.database.cii_db.schemas import (
    PicturesCreateSchema, PicturesUpdateSchema)

__all__ = ['PicturesQuery']


class PicturesQuery(
    BaseDAO[PicturesModel, PicturesCreateSchema, PicturesUpdateSchema]
):
    model = PicturesModel
