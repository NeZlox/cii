from functools import wraps

from fastapi import HTTPException

from src.config import settings
from src.exceptions import RequestHandlingError
from src.logger import logger


def error_handler(route_path: str = ""):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get("request")  # Получаем запрос, если передан явно
            token = request.headers.get("token") if request else None

            # Получение всех query-параметров и их значений из kwargs, если они строковые
            query_params = {k: v for k, v in kwargs.items() if isinstance(v, str)}

            try:
                return await func(*args, **kwargs)
            except HTTPException as e:
                msg = f"{route_path or func.__name__} - Handled error"
                extra = {
                    "api_method": request.method if request else "UNKNOWN",
                    "query_params": query_params,
                    "error": str(e),
                    "token": token
                }
                if e.status_code < 500:
                    logger.info(msg, extra=extra, exc_info=True)
                else:
                    logger.error(msg, extra=extra, exc_info=True)
                if e.status_code < 500 or settings.MODE != 'PROD':
                    raise e
                raise RequestHandlingError from e
            except Exception as e:
                msg = f"{route_path or func.__name__} - Unknown error"
                extra = {
                    "api_method": request.method if request else "UNKNOWN",
                    "query_params": query_params,
                    "error": str(e),
                    "token": token
                }
                logger.critical(msg, extra=extra, exc_info=True)
                raise RequestHandlingError from e

        return wrapper

    return decorator
