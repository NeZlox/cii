from src.database.base_DAO import BaseDAO
from src.database.cii_db.models import ModelModel
from src.database.cii_db.schemas import (ModelCreateSchema,
                                         ModelUpdateSchema)

__all__ = ['ModelQuery']


class ModelQuery(
    BaseDAO[ModelModel, ModelCreateSchema, ModelUpdateSchema]
):
    model = ModelModel
