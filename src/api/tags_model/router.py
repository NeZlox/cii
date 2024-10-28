from io import BytesIO

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi_versioning import version
from PIL import Image

from src.api.error_handler import error_handler
from src.api.tags_model.schemas import PredictedTagsResponse
from src.api.tags_model.service import TagsService
from src.logger import logger

__all__ = ('router',)
router = APIRouter(tags=["Models for create tags"], prefix="/tags_models")


@router.post("/vit", response_model=PredictedTagsResponse)
@version(1)
async def upload_image_vit(file: UploadFile = File(...)):
    if file is None or file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Только JPEG и PNG изображения поддерживаются.")

    try:
        image_data = await file.read()
        image = Image.open(BytesIO(image_data))

        predicted_tags = await TagsService.predict_tags_vit(image)

        return PredictedTagsResponse(
            filename=file.filename,
            predicted_tags=predicted_tags[0]
        )
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail="Ошибка при обработке изображения.")


@router.post("/clip", response_model=PredictedTagsResponse)
@version(1)
async def upload_image_clip(file: UploadFile):
    if file is None or file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Только JPEG и PNG изображения поддерживаются.")

    try:
        image_data = await file.read()
        image = Image.open(BytesIO(image_data))

        predicted_tags = await TagsService.predict_tags_clip(image)

        return PredictedTagsResponse(
            filename=file.filename,
            predicted_tags=predicted_tags[0]
        )
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail="Ошибка при обработке изображения.")


@router.post("/combined/intersection", response_model=PredictedTagsResponse)
@version(1)
async def upload_image_intersection(file: UploadFile = File(...)):
    if file is None or file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Только JPEG и PNG изображения поддерживаются.")

    try:
        image_data = await file.read()
        image = Image.open(BytesIO(image_data))

        # Получаем предсказанные теги обеих моделей
        vit_tags = await TagsService.predict_tags_vit(image)
        clip_tags = await TagsService.predict_tags_clip(image)

        # Вычисляем пересечение
        intersection_tags = list(set(vit_tags[0]) & set(clip_tags[0]))

        return PredictedTagsResponse(
            filename=file.filename,
            predicted_tags=intersection_tags
        )
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail="Ошибка при обработке изображения.")


@router.post("/combined/union", response_model=PredictedTagsResponse)
@version(1)
async def upload_image_union(file: UploadFile = File(...)):
    if file is None or file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Только JPEG и PNG изображения поддерживаются.")

    try:
        image_data = await file.read()
        image = Image.open(BytesIO(image_data))

        # Получаем предсказанные теги обеих моделей
        vit_tags = await TagsService.predict_tags_vit(image)
        clip_tags = await TagsService.predict_tags_clip(image)

        # Вычисляем объединение
        union_tags = list(set(vit_tags[0]).union(set(clip_tags[0])))

        return PredictedTagsResponse(
            filename=file.filename,
            predicted_tags=union_tags
        )
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail="Ошибка при обработке изображения.")
