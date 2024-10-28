import asyncio
import os
from typing import List

import aiofiles
from bs4 import BeautifulSoup
from pydantic import BaseModel

from src.utils import BaseAioHttpService

__all__ = ['ParseService']


class ImageInfo(BaseModel):
    width: int
    height: int
    img_url: str
    img_data: bytes
    path: str


class ParseService(BaseAioHttpService):
    _URL_TEMPLATE = 'https://safebooru.org/index.php?page=post&s=view&id={}'

    @classmethod
    def get_url_page(cls, post_id: int) -> str:
        return cls._URL_TEMPLATE.format(post_id)

    @classmethod
    async def get_image(cls, soup: BeautifulSoup, name_file: str) -> ImageInfo:
        """Извлекает информацию об изображении и загружает его асинхронно."""
        img_tag = soup.find('img', {'id': 'image'})

        # Безопасное извлечение атрибутов изображения
        width = img_tag.get('width')
        height = img_tag.get('height')
        img_url = img_tag.get('src')

        # Загрузка данных изображения
        img_data = await BaseAioHttpService.make_read_request(img_url, method='GET')

        # Определение пути для сохранения изображения
        path = (os.path.join(os.getcwd(), 'src', 'images', f'{name_file}.jpg')).replace('\\', '/')

        # Сохранение изображения в файловую систему
        async with aiofiles.open(path, 'wb') as file:
            await file.write(img_data)

        return ImageInfo(width=width, height=height, img_url=img_url, img_data=img_data, path=path)

    @classmethod
    async def get_tags(cls, soup: BeautifulSoup) -> List[str]:
        """Извлекает список тегов из HTML-страницы."""
        tags_ul = soup.find('ul', id='tag-sidebar')
        tags = []

        if not tags_ul:
            return tags

        for tag in tags_ul.find_all('li'):
            tag_count = tag.find('span', class_='tag-count')
            if tag_count:
                tag_link = tag.find_all('a')[-1]
                tags.append(tag_link.text)
        return tags

    @classmethod
    async def binary_search_max_valid(cls, low: int, high: int) -> int:
        """Бинарный поиск для нахождения максимального значения, при котором div 'post-list' не равен None."""

        def is_valid_soup(parsed_soup: BeautifulSoup):
            """Проверка, существует ли div с id 'post-list'."""
            if parsed_soup.find('div', {'id': 'post-list'}) is None:
                return True
            return False

        while low < high:
            mid = (low + high + 1) // 2
            url = cls._URL_TEMPLATE.format(mid)
            # print(f"Checking URL: {url}")
            try:
                text = await cls.make_text_request(url=url, method='GET')
                soup = BeautifulSoup(text, 'lxml')

                if is_valid_soup(soup):
                    low = mid  # Если div найден, ищем дальше выше
                else:
                    high = mid - 1  # Иначе ищем ниже

            except Exception as e:
                print(f"Error with URL {url}: {e}")
                await asyncio.sleep(2)  # В случае ошибки ждем 2 секунды

        return low

    @classmethod
    async def get_page(cls, url: str) -> BeautifulSoup:
        """Получение HTML-страницы по URL."""
        text_response = await cls.make_text_request(url=url, method='GET')
        soup = BeautifulSoup(text_response, 'lxml')
        return soup
