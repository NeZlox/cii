from fastapi import APIRouter, HTTPException, Query
from fastapi_versioning import version

from src.api.search.schemas import ResponsePictures
from src.api.search.service import ElasticService
from src.database.cii_db.queries import PicturesQuery
from src.logger import logger
from src.config import settings

router = APIRouter(tags=["Search images"], prefix="/search")


@router.get("", response_model=ResponsePictures)
@version(1)
async def start_search(
        search_string: str = None,
        page: int = Query(default=1, description="Начальная страница", ge=1),
        page_size: int = Query(default=10, description="Количество элементов на странице", ge=1, le=100),
):
    """Запускает поиск подходящий изображений."""

    try:
        result_ids = None
        if search_string and search_string.strip():
            search_string = " ".join(search_string.split())
            result_ids = await ElasticService.search(
                search_string=search_string, limit=page_size,
                index_name=settings.ELASTIC_INDEX
            )

        results = await PicturesQuery.get_pictures_with_tags_by_ids(
            limit=page_size,
            offset=page_size * (page - 1),
            image_ids=result_ids
        )
        total = await PicturesQuery.get_total_by_filter(
            image_ids=result_ids
        )

        return ResponsePictures(data=results, total=total)


    except Exception as e:
        logger.exception(f"Ошибка при поиске: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при поиске")
