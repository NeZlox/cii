import asyncio

from src.api.search.service import ElasticService
from src.config import settings
from src.database.cii_db.queries import TransactionSessionQuery
from src.database.cii_db.schemas import PicturesCreateSchema
from src.parse.service import ParseService
from src.utils import BaseAioHttpService
from src.utils.elastic_service import BaseElasticService

# Количество одновременных задач
MAX_CONCURRENT_TASKS = 4


# Функция, которая будет обрабатывать посты
async def process_posts(post_id: int):
    try:
        print(f"Processing post {post_id}")
        name_file_img = f'image_{post_id}'
        url_page = ParseService.get_url_page(post_id=post_id)

        soup = await ParseService.get_page(url=url_page)
        image_info = await ParseService.get_image(soup=soup, name_file=name_file_img)
        tags_image = await ParseService.get_tags(soup=soup)

        id_img = await TransactionSessionQuery.insert_new_picture(
            info_picture=PicturesCreateSchema(
                resolution_width=image_info.width,
                resolution_height=image_info.height,
                url_page=url_page,
                url_image=image_info.img_url,
                path=image_info.path,
            ),
            tags=tags_image
        )
        # Сохранение в эластике
        await ElasticService.add_data(
            index_name=settings.ELASTIC_INDEX,
            id_image=id_img,
            tags_image=tags_image
        )
    except Exception as e:
        pass
        print(f"Error processing post {post_id}: {e}")


# Функция-обработчик с ограничением по одновременным задачам
async def bounded_process_posts(sem: asyncio.Semaphore, post_id: int):
    async with sem:
        await process_posts(post_id)


async def main():
    BaseAioHttpService.set_session()
    connect_elastic = BaseElasticService()
    connect_elastic.connect(
        host=settings.ELASTIC_URL,
        verify_certs=False)
    max_value = 10_000_000
    min_value = 1

    # Максимальное ограничение
    max_constraint = await ParseService.binary_search_max_valid(low=min_value, high=max_value)

    # Ограничение одновременных задач
    sem = asyncio.Semaphore(MAX_CONCURRENT_TASKS)

    tasks = []
    # 1140
    for i in range(1, 1000):
        await process_posts(i)
        # tasks.append(bounded_process_posts(sem, i))

    # Запуск всех задач параллельно
    # await asyncio.gather(*tasks)

    await BaseAioHttpService.close_session()


if __name__ == "__main__":
    asyncio.run(main())

"""
python -m src.parse.main 
alembic upgrade head  
alembic downgrade -1 
alembic revision --autogenerate -m "initial_migration"   
"""
