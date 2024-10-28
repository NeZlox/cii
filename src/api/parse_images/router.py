from fastapi import APIRouter, HTTPException, Query
from fastapi_versioning import version

from src.api.error_handler import error_handler
from src.api.parse_images.service import ParseService
from src.logger import logger

router = APIRouter(tags=["Parse images"], prefix="/parse")


@router.post("/start")
@version(1)
async def start_parsing(
        start_id: int = Query(..., description="Начальный ID поста для парсинга"),
        end_id: int = Query(..., description="Конечный ID поста для парсинга")
):
    """Запускает асинхронный парсер для обработки изображений."""
    if start_id >= end_id:
        raise HTTPException(status_code=400, detail="start_id должен быть меньше end_id")

    try:
        # Запускаем задачу парсинга изображений
        await ParseService.start_parsing(start_id=start_id, end_id=end_id)
        return {"status": "Парсер запущен успешно", "start_id": start_id, "end_id": end_id}
    except Exception as e:
        logger.exception(f"Ошибка при запуске парсера: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при запуске парсера")
