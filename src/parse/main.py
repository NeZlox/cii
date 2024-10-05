import asyncio
from src.parse.service import ParseService
from src.utils import BaseAioHttpService
from concurrent.futures import ThreadPoolExecutor, as_completed

sem = asyncio.Semaphore(50)


# Функция, которая будет обрабатывать посты
async def process_posts(post_id: int):
    # Логика обработки поста
    async with sem:
        try:
            print(f"Processing post {post_id}")
            soup = await ParseService.get_page(url=ParseService.get_url_page(post_id=post_id))

            image_info = await ParseService.get_image(soup=soup, name_file=f'image_{post_id}')
            tags_image = await ParseService.get_tags(soup=soup)
        except:
            print(f"Error post {post_id}")


async def main():
    BaseAioHttpService.set_session()
    max_value = 10_000_000
    min_value = 1
    max_constraint = await ParseService.binary_search_max_valid(low=min_value, high=max_value)
    max_constraint = 1_000
    for i in range(min_value, max_constraint + 1):
        await process_posts(i)

    await BaseAioHttpService.close_session()


if __name__ == "__main__":
    asyncio.run(main())
    # python -m src.parse.main
