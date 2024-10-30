import asyncio
from typing import Optional

from pydantic import BaseModel, Field

from src.database.cii_db.queries import TransactionSessionQuery
from src.database.cii_db.schemas import PicturesCreateSchema
from src.parse.service import ParseService as BaseParseService


class ParsingResultSchema(BaseModel):
    start_id: int = Field(..., description="Начальный ID поста")
    end_id: int = Field(..., description="Конечный ID поста")


class ParseService(BaseParseService):
    MAX_CONCURRENT_TASKS = 4

    @classmethod
    async def start_parsing(cls, start_id: Optional[int] = None, end_id: Optional[int] = None) -> ParsingResultSchema:
        """Запускает асинхронный парсер для обработки изображений."""
        if start_id is None:
            start_id = 1
        if end_id is None:
            max_value = 10_000_000
            end_id = await cls.binary_search_max_valid(low=start_id, high=max_value)

        # Более стабильный способ
        for post_id in range(start_id, end_id + 1):
            await cls.process_post(post_id)

        return ParsingResultSchema(
            start_id=start_id,
            end_id=end_id
        )
        # Тестирование

        # Инициализация очереди для ID постов
        post_id_queue = asyncio.Queue()
        for post_id in range(start_id, end_id + 1):
            await post_id_queue.put(post_id)

        # Запускаем задачи парсинга с использованием семафора
        tasks = [
            cls.worker(post_id_queue)
            for _ in range(cls.MAX_CONCURRENT_TASKS)
        ]

        await asyncio.gather(*tasks)

    @classmethod
    async def worker(cls, post_id_queue: asyncio.Queue):
        """Обработчик задач из очереди с ограничением по количеству задач."""
        while not post_id_queue.empty():
            post_id = await post_id_queue.get()
            await cls.process_post(post_id)
            post_id_queue.task_done()

    @classmethod
    async def process_post(cls, post_id: int):
        """Процесс парсинга одного поста."""
        try:
            print(f"Обработка поста {post_id}")
            url_page = cls.get_url_page(post_id=post_id)

            # Получение HTML страницы и парсинг
            soup = await cls.get_page(url=url_page)
            image_info = await cls.get_image(soup=soup, name_file=f"image_{post_id}")
            tags_image = await cls.get_tags(soup=soup)

            # Сохранение данных в базе
            await TransactionSessionQuery.insert_new_picture(
                info_picture=PicturesCreateSchema(
                    resolution_width=image_info.width,
                    resolution_height=image_info.height,
                    url_page=url_page,
                    url_image=image_info.img_url,
                    path=image_info.path,
                ),
                tags=tags_image
            )
        except Exception as e:
            print(f"Ошибка при обработке поста {post_id}: {e}")
