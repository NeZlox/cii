import asyncio

from src.utils import BaseAioHttpService

url = 'https://anime-pictures.net/posts/839716?lang=ru'
async def main():
    t = BaseAioHttpService()
    print(t)
    t.set_session()
    url = 'https://api.steam-currency.ru/currency/USD:RUB'
    tt = await t.make_json_request(url=url, method='GET')


if __name__ == "__main__":
    asyncio.run(main())
    # python -m src.parse.main
