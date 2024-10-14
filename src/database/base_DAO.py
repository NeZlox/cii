from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

from pydantic import BaseModel
from sqlalchemy import and_, asc, delete, desc, insert, or_, select, update
from sqlalchemy.exc import SQLAlchemyError

from src.database.cii_db.database import Base
from src.database.cii_db.database import \
    async_session_maker as sessionmaker
from src.exceptions import (CannotDeleteDataToDatabase,
                            CannotFindAllDataToDatabase,
                            CannotFindOneOrNoneDataToDatabase,
                            CannotInsertDataToDatabase,
                            CannotUpdateDataToDatabase)
from src.logger import logger

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class SingletonMeta(type):
    """Метакласс для реализации паттерна Singleton"""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)

        return cls._instances[cls]


class BaseDAO(Generic[ModelType, CreateSchemaType, UpdateSchemaType], metaclass=SingletonMeta):
    model = None
    async_session_maker = sessionmaker

    @classmethod
    async def get_async_session_maker(cls):
        return cls.async_session_maker()

    @classmethod
    async def create_sortirovka(cls, sort: Dict[str, str], curr_model=None):
        order_by_model = []
        for field, direction in sort.items():
            if direction == 'asc':
                order_by_model.append(asc(getattr(curr_model if curr_model else cls.model, field)))
            elif direction == 'desc':
                order_by_model.append(desc(getattr(curr_model if curr_model else cls.model, field)))

        return order_by_model

    @classmethod
    async def create_filtrovka(cls, filter_dict: Dict[str, Dict[str, Any]], curr_model=None):
        filter_by_model = []

        for field, filter_data in filter_dict.items():
            sub_filter = []

            for filter_key, filter_value in filter_data.items():
                if filter_key == 'ge':
                    sub_filter.append(getattr(cls.model if curr_model is None else curr_model, field) >= filter_value)
                elif filter_key == 'gt':
                    sub_filter.append(getattr(cls.model if curr_model is None else curr_model, field) > filter_value)
                elif filter_key == 'le':
                    sub_filter.append(getattr(cls.model if curr_model is None else curr_model, field) <= filter_value)
                elif filter_key == 'lt':
                    sub_filter.append(getattr(cls.model if curr_model is None else curr_model, field) < filter_value)
                elif filter_key == 'e':
                    sub_filter.append(getattr(cls.model if curr_model is None else curr_model, field) == filter_value)
                elif filter_key == 'like':
                    sub_filter.append(
                        getattr(cls.model if curr_model is None else curr_model, field).like(filter_value))
                elif filter_key == 'ilike':
                    sub_filter.append(
                        getattr(cls.model if curr_model is None else curr_model, field).ilike(filter_value))

            compare = filter_data.get('and_', None)
            if compare == 1:
                filter_by_model.append(and_(*sub_filter))
            elif compare == 0:
                filter_by_model.append(or_(*sub_filter))
            else:
                filter_by_model.append(*sub_filter)
        return filter_by_model

    @classmethod
    async def find_one_or_none(cls, **filter_by) -> Optional[ModelType]:

        async with cls.async_session_maker() as session:
            try:
                stmt = select(cls.model).filter_by(**filter_by)
                result = await session.execute(stmt)
                return result.scalars().one_or_none()


            except (SQLAlchemyError, Exception) as e:
                await session.rollback()
                if isinstance(e, SQLAlchemyError):

                    msg = "BaseDAO Database error"

                else:

                    msg = "BaseDAO Unknown error"

                msg += ": Cannot find one or none data"

                extra = {

                    "query": filter_by,
                    "error": e

                }

                logger.error(msg, extra=extra, exc_info=True)
                raise CannotFindOneOrNoneDataToDatabase

    @classmethod
    async def find_all(cls, **filter_by) -> List[ModelType]:
        async with cls.async_session_maker() as session:
            try:
                query = select(cls.model.__table__.columns).filter_by(**filter_by)
                result_orm = await session.execute(query)
                result = result_orm.mappings().all()

                return result


            except (SQLAlchemyError, Exception) as e:
                await session.rollback()
                if isinstance(e, SQLAlchemyError):

                    msg = "BaseDAO Database error"

                else:

                    msg = "BaseDAO Unknown error"

                msg += ": Cannot find all data"

                extra = {

                    "query": filter_by,
                    "error": e

                }

                logger.error(msg, extra=extra, exc_info=True)
                raise CannotFindAllDataToDatabase

    @classmethod
    async def insert_one(cls, obj_in: Union[CreateSchemaType, Dict[str, Any]]) -> Optional[ModelType]:
        if isinstance(obj_in, dict):
            create_data = obj_in
        else:
            create_data = obj_in.model_dump(exclude_unset=True)

        async with cls.async_session_maker() as session:
            try:
                stmt = insert(cls.model).values(**create_data).returning(cls.model.__table__.columns)
                result = await session.execute(stmt)
                await session.commit()
                return_result = result.mappings().first()
                return return_result

            except (SQLAlchemyError, Exception) as e:
                await session.rollback()
                if isinstance(e, SQLAlchemyError):

                    msg = "BaseDAO Database error"

                else:

                    msg = "BaseDAO Unknown error"

                msg += ": Cannot insert data"

                extra = {

                    "query": create_data,
                    "error": e

                }

                logger.error(msg, extra=extra, exc_info=True)
                raise CannotInsertDataToDatabase

    @classmethod
    async def update(cls, obj_in: Union[UpdateSchemaType, Dict[str, Any]], id: int = None) -> Optional[ModelType]:

        if isinstance(obj_in, dict):
            update_data = obj_in
            if id is None:
                id = obj_in.get("id", None)
            update_data.pop("id", None)
        else:
            update_data = obj_in.model_dump(exclude_unset=True, exclude={'id'})
            if id is None:
                id = obj_in.dict().get("id", None)

        async with cls.async_session_maker() as session:
            try:
                stmt = (
                    update(cls.model)
                    .where(cls.model.id == id)
                    .values(**update_data)
                    .returning(cls.model)
                )

                result = await session.execute(stmt)

                await session.commit()

                return result.scalars().one()

            except (SQLAlchemyError, Exception) as e:
                await session.rollback()
                if isinstance(e, SQLAlchemyError):

                    msg = "BaseDAO Database error"

                else:

                    msg = "BaseDAO Unknown error"

                msg += ": Cannot update data"

                extra = {

                    "query": {"id": id, "update_data": update_data},
                    "error": e

                }

                logger.error(msg, extra=extra, exc_info=True)
                raise CannotUpdateDataToDatabase

    @classmethod
    async def delete(cls, **filter_by) -> bool:
        async with cls.async_session_maker() as session:
            try:
                stmt = delete(cls.model).filter_by(**filter_by)
                result = await session.execute(stmt)
                if result.rowcount == 0:
                    await session.rollback()
                    return False

                await session.commit()

                return True


            except (SQLAlchemyError, Exception) as e:
                await session.rollback()
                if isinstance(e, SQLAlchemyError):

                    msg = "BaseDAO Database error"

                else:

                    msg = "BaseDAO Unknown error"

                msg += ": Cannot delete data"

                extra = {

                    "query": filter_by,
                    "error": e

                }

                logger.error(msg, extra=extra, exc_info=True)
                raise CannotDeleteDataToDatabase


"""
async def get_async_session_maker():
    return await BaseDAO.get_async_session_maker()
"""
