from fastapi import APIRouter

from src.api.parse_images import router_parse_images
from src.api.tags_model import router_tags_model

router = APIRouter()

router.include_router(router_tags_model)
router.include_router(router_parse_images)
