from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi_versioning import version
from pydantic import BaseModel, Field

from src.api.error_handler import error_handler
from src.api.parse_images.service import ParseService
from src.logger import logger

router = APIRouter(tags=["Parse images"], prefix="/parse")


class StartParsingRequestSchema(BaseModel):
    start_id: Optional[int] = Field(default=None, description="Начальный ID поста для парсинга")
    end_id: Optional[int] = Field(default=None, description="Конечный ID поста для парсинга")


class StartParsingResponseSchema(BaseModel):
    status: str = Field(..., description="Статус запуска парсера")
    start_id: Optional[int] = Field(..., description="Начальный ID поста")
    end_id: Optional[int] = Field(..., description="Конечный ID поста")


@router.post("/start", response_model=StartParsingResponseSchema)
@version(1)
async def start_parsing(
        query_params: StartParsingRequestSchema = Depends(StartParsingRequestSchema)
):
    """Запускает асинхронный парсер для обработки изображений."""
    if query_params.start_id is not None and query_params.end_id is not None and query_params.start_id > query_params.end_id:
        raise HTTPException(status_code=400, detail="start_id должен быть меньше end_id")

    try:

        # Запускаем задачу парсинга изображений
        await ParseService.start_parsing(start_id=query_params.start_id, end_id=query_params.end_id)

        return StartParsingResponseSchema(
            status="Парсер запущен успешно",
            start_id=query_params.start_id,
            end_id=query_params.end_id
        )
    except Exception as e:
        logger.exception(f"Ошибка при запуске парсера: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при запуске парсера")
