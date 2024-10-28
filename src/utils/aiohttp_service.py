import asyncio
import atexit
from socket import AF_INET
from typing import Any, Callable, Literal

import aiohttp

from src.exceptions import (ErrorBaseAioHttpServiceBadRequest,
                            ErrorBaseAioHttpServiceRequestTimeout,
                            ErrorBaseAioHttpServiceServerError,
                            ErrorBaseAioHttpServiceUnavailable)
from src.logger import logger
from src.utils.singleton_meta import SingletonMeta

SIZE_POOL_AIOHTTP = 200

__all__ = ['BaseAioHttpService']


class BaseAioHttpService(metaclass=SingletonMeta):
    _session = None

    @classmethod
    def set_session(cls):
        """Метод класса для установки сессии."""
        if cls._session is None:
            timeout = aiohttp.ClientTimeout(total=10)
            connector = aiohttp.TCPConnector(family=AF_INET, limit_per_host=SIZE_POOL_AIOHTTP)
            cls._session = aiohttp.ClientSession(timeout=timeout, connector=connector)

    @classmethod
    def get_session(cls) -> aiohttp.ClientSession:
        if cls._session is None:
            cls.set_session()
        return cls._session

    @classmethod
    async def close_session(cls) -> None:
        logger.info(msg='d')
        if cls._session:
            await cls._session.close()
            cls._session = None

    @classmethod
    def close_session_sync(cls) -> None:
        """Синхронная обертка для закрытия сессии"""
        if cls._session:
            asyncio.run(cls.close_session())

    @classmethod
    async def _make_request(cls, url: str, method: Literal["GET", "POST"], headers: dict = None,
                            params: dict = None, data: dict = None, json: dict = None,
                            response_handler: Callable[[aiohttp.ClientResponse], Any] = None) -> Any:
        """Общая функция для выполнения HTTP-запроса с повторными попытками"""
        for attempt in range(1, 4):
            try:
                # logger.info(f"Sending {method} request to {url} with headers {headers}, params {params}, data {data} and json {json}")
                async with cls._session.request(
                        method, url,
                        headers=headers, params=params, data=data, json=json, timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    response = await cls._handle_response(response)
                    # logger.info("Request successful, processing data")
                    return await response_handler(response) if response_handler else None

            except asyncio.TimeoutError:
                logger.error("Request timed out")
                if attempt == 3:
                    raise ErrorBaseAioHttpServiceRequestTimeout("Request timed out")
                await asyncio.sleep(2 ** attempt)

            except aiohttp.ClientError as e:
                logger.error(f"Client error: {e}")
                raise ErrorBaseAioHttpServiceBadRequest(f"Client error: {e}")

            except Exception as e:
                if not isinstance(e, ErrorBaseAioHttpServiceUnavailable):
                    logger.error(f"Unexpected error: {e}")
                    raise ErrorBaseAioHttpServiceUnavailable(f"Unexpected error: {e}")
                logger.error(f"Service error: {e}")
                raise e

    @classmethod
    async def make_json_request(cls, url: str, method: Literal["GET", "POST"], headers: dict = None,
                                params: dict = None, data: dict = None, json: dict = None) -> dict:
        """Выполнение HTTP-запроса, ожидающего JSON в ответе"""
        return await cls._make_request(url, method, headers, params, data, json,
                                       response_handler=lambda response: response.json())

    @classmethod
    async def make_text_request(cls, url: str, method: Literal["GET", "POST"], headers: dict = None,
                                params: dict = None, data: dict = None, json: dict = None) -> str:
        """Выполнение HTTP-запроса, ожидающего текст в ответе"""
        return await cls._make_request(url, method, headers, params, data, json,
                                       response_handler=lambda response: response.text())

    @classmethod
    async def make_read_request(cls, url: str, method: Literal["GET", "POST"], headers: dict = None,
                                params: dict = None, data: dict = None, json: dict = None) -> bytes:
        """Выполнение HTTP-запроса, ожидающего изображение в ответе"""
        return await cls._make_request(url, method, headers, params, data, json,
                                       response_handler=lambda response: response.read())

    @classmethod
    async def _handle_response(cls, response: aiohttp.ClientResponse) -> aiohttp.ClientResponse:
        """Обработка ответа от сервера"""
        # print(response)
        if response.status == 200:
            return response
        elif 400 <= response.status < 500:
            logger.error(f"Client error: {response.status}, text: {await response.text()}")
            raise ErrorBaseAioHttpServiceBadRequest(f"Client error: {response.status}")
        elif 500 <= response.status < 600:
            logger.error(f"Server error: {response.status}")
            raise ErrorBaseAioHttpServiceServerError(f"Server error: {response.status}")


atexit.register(BaseAioHttpService.close_session_sync)
