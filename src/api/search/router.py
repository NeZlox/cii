from fastapi import APIRouter, HTTPException
from fastapi_versioning import version

from src.api.search.schemas import ResponsePictures
from src.api.search.service import ElasticService
from src.database.cii_db.queries import PicturesQuery
from src.logger import logger
from src.config import settings

router = APIRouter(tags=["Search images"], prefix="/search")


@router.get("/", response_model=ResponsePictures)
@version(1)
async def start_search(
        search_string: str,
        limit: int,
):
    """Запускает поиск подходящий изображений."""

    try:
        search_string = " ".join(search_string.split())
        result_ids = await ElasticService.search(
            search_string=search_string, limit=limit,
            index_name=settings.ELASTIC_INDEX
        )

        results = await PicturesQuery.get_pictures_with_tags_by_ids(image_ids=result_ids)

        return ResponsePictures(data=results)


    except Exception as e:
        logger.exception(f"Ошибка при поиске: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при поиске")
