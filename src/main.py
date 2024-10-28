import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi_versioning import VersionedFastAPI

from src.api import router_api
from src.api.tags_model.service import TagsService
from src.config import settings
from src.logger import logger
from src.utils import BaseAioHttpService


@asynccontextmanager
async def lifespan(app: FastAPI):
    # при запуске

    logger.info(msg="Server is starting")

    session_manager_aiohttp = BaseAioHttpService()
    session_manager_aiohttp.set_session()
    await TagsService.init_service()
    try:
        yield
    finally:
        # При выключении
        await session_manager_aiohttp.close_session()
        logger.critical("Server is down")


app = FastAPI(
    title="Smart Art Search API",
    lifespan=lifespan
)

app.include_router(router_api)

app = VersionedFastAPI(
    app,
    version_format='{major}',
    prefix_format='/api/v{major}',
    lifespan=lifespan
)


@app.get("/health", status_code=status.HTTP_200_OK)
async def health():
    return "ok"


if settings.MODE == "PROD":
    origins = [
        "http://digiseller_orders_frontend:80",
        "http://localhost:8001",
        "http://localhost:3000"
    ]



else:
    origins = [
        "http://digiseller_orders_frontend:80",
        "http://localhost:3000",
        "http://127.0.0.1:8002",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # ["*"] origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "PATCH", "OPTIONS", "PUT"],  # "OPTIONS","PUT",
    allow_headers=["*"]
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    # При подключении Prometheus + Grafana подобный лог не требуется
    logger.info("Request handling time", extra={
        "process_time": round(process_time, 4),
        "api_method": request.method,
        "api_request": request.url,
    })
    return response


if settings.MODE == "PROD":
    pass
# app.add_middleware(HTTPSRedirectMiddleware)

# uvicorn main:app --reload

# ipconfig
# uvicorn main:app --host 127.0.0.1 --port 8000 --reload
# для продакшена и только на линуксе gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000

# celery -A src.tasks.tasks:celery worker --loglevel=INFO --pool=solo
# celery -A src.tasks.tasks:celery flower
# localhost:5555
