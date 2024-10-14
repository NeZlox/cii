import asyncio
import os

from src.parse.service import ParseService
from src.utils import BaseAioHttpService
from src.database.cii_db.queries import TransactionSessionQuery
from src.database.cii_db.schemas import PicturesCreateSchema

# Количество одновременных задач
MAX_CONCURRENT_TASKS = 10


# Функция, которая будет обрабатывать посты
async def process_posts(post_id: int):
    try:
        print(f"Processing post {post_id}")
        name_file_img = f'image_{post_id}'
        url_page = ParseService.get_url_page(post_id=post_id)

        soup = await ParseService.get_page(url=url_page)
        image_info = await ParseService.get_image(soup=soup, name_file=name_file_img)
        tags_image = await ParseService.get_tags(soup=soup)

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
        pass
        # print(f"Error processing post {post_id}: {e}")


# Функция-обработчик с ограничением по одновременным задачам
async def bounded_process_posts(sem: asyncio.Semaphore, post_id: int):
    async with sem:
        await process_posts(post_id)


async def main():
    BaseAioHttpService.set_session()
    max_value = 10_000_000
    min_value = 1
    max_constraint = await ParseService.binary_search_max_valid(low=min_value, high=max_value)

    # Ограничение одновременных задач
    sem = asyncio.Semaphore(MAX_CONCURRENT_TASKS)

    tasks = []
    for i in range(min_value, max_constraint):
        tasks.append(bounded_process_posts(sem, i))

    # Запуск всех задач параллельно
    await asyncio.gather(*tasks)

    await BaseAioHttpService.close_session()


if __name__ == "__main__":
    asyncio.run(main())


"""
python -m src.parse.main 
alembic upgrade head  
alembic downgrade -1 
alembic revision --autogenerate -m "initial_migration"   
"""