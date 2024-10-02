import json
import logging
import re
import time
from typing import List

import asyncio
import aiohttp

from bs4 import BeautifulSoup


class BHParser:
    def __init__(self):
        self.base_url = 'https://www.bethowen.ru'
        self.default_sleep = 0
        self.default_headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
        }
        self.session = aiohttp.ClientSession(headers=self.default_headers)

    async def get(self, url, is_json: bool=False, only_text: bool=False, **kwargs):
        time.sleep(self.default_sleep)
        async with self.session.get(url, **kwargs) as resp:
            html = await resp.text()
        if is_json:
            return json.loads(html)
        if only_text:
            return html
        return BeautifulSoup(html, 'html.parser')

    async def get_categories(self) -> List[tuple]:
        """Получение всех категорий для настраиваемого парсинга"""

        soup = await self.get('https://www.bethowen.ru/')
        categories = list()
        html_nav_list = soup.find_all('a', {'class': 'js-ixi-nav-link'})[1:-7]
        for nav in html_nav_list:
            cat_url = nav.get('href')
            cat_name = nav.getText()
            if not nav.get('title'):
                nav_group = cat_name
                categories.append((cat_url, cat_name))
            else:
                categories.append((cat_url, nav_group + " | " + cat_name))
        return categories

    async def get_shops(self) -> List[tuple]:
        """Получение всех торговых точек для отслеживания товаров и дальнейшей записи в БД"""

        soup = await self.get('https://www.bethowen.ru/shops/')
        shops = list()
        html_shop_list = soup.find_all('div', {'class': 'dgn-flex dgn-border-b dgn-py-6'})
        for html_shop in html_shop_list:
            html_shop_url = html_shop.find_next('a')
            shop_url = html_shop_url.get('href')
            shop_id = int(re.search(r'\d+', shop_url).group())
            shop_addr = html_shop_url.find_next('div', {'class': 'dgn-font-semibold dgn-leading-5'}).getText()
            shop_tel = html_shop.find_next('a', {'rel': 'nofollow'}).getText()
            shops.append((shop_id, shop_url, shop_addr, shop_tel))
        return shops

    async def get_products_ids_from_category(self, url: str) -> List[str]:
        soup = await self.get(url)
        htm_section_with_product_id = soup.find_all('section', {'class': 'bth-card-element dgn-relative'})
        product_ids = list()
        for tag in htm_section_with_product_id:
            product_ids.append(tag.get('data-product-id'))
        return product_ids

    async def get_products_general_info_from_api(self, product_ids: List[str]) -> List[dict]:
        if product_ids:
            json_products_info = await self.get('https://www.bethowen.ru/api/local/v1/catalog/list?' +
                                                'limit=20&' +
                                                'offset=0&' +
                                                'sort_type=popular&' +
                                                'id[]=' + "&id[]=".join(product_ids),
                                                is_json=True)
            product_offers = list()
            for product in json_products_info.get('products'):
                product_offers.append({'id': product.get('id'),
                                       'name': product.get('name'),
                                       'link': product.get('link'),
                                       'offers': product.get('offers')})
            return product_offers

    async def get_product_detail_info_from_api(self, product_id: str, product_link: str, product_name: str) -> tuple:
        """Получает детальную информацию только у товаров в offers, а не у товаров на главной странице каталога"""
        full_detail_product_info = await self.get(f'https://www.bethowen.ru/api/local/v1/catalog/offers/{product_id}/details', is_json=True)
        product = (int(product_id),
                   product_link,
                   product_name,
                   full_detail_product_info.get('size'),
                   full_detail_product_info.get('retail_price'),
                   full_detail_product_info.get('discount_price'),
                   full_detail_product_info.get('vendor_code'),
                   full_detail_product_info.get('availability_info')
                   )
        return product

    async def get_max_page_in_category(self, url: str) -> int:
        soup = await self.get(url)
        pagination = soup.find_all('div', {'class': 'module-pagination 2'})
        if pagination:
            max_page = pagination[0].find_all('a')[-1].getText()
            return int(max_page)
        else:
            return 1

    async def get_product_ids_by_page(self, url: str, page: int):
        url += f'?PAGEN_1={page}'
        return await self.get_products_ids_from_category(url)

    async def get_town(self, town_name) -> List[dict]:
        towns = await self.get(f'https://www.bethowen.ru/api/local/v1/cities/search?term={town_name}&city_type=all', is_json=True)
        return towns.get('cities')

    async def get_products_in_category(self, url: str, page: int):
        product_ids = await self.get_product_ids_by_page(url, page)
        product_offers = await self.get_products_general_info_from_api(product_ids)
        parsed_product = list()
        for general_product in product_offers:
            parse_tasks = list()
            for offer in general_product.get('offers'):
                parse_tasks.append(self.get_product_detail_info_from_api(offer.get('id'),
                                                                         general_product.get('link'),
                                                                         general_product.get('name')))
            parsed_product.extend(await asyncio.gather(*parse_tasks))
        return parsed_product


    async def close(self):
        await self.session.close()


async def main():
    logging.basicConfig(level=logging.DEBUG)
    bh_parser = BHParser()
    await bh_parser.close()

if __name__ == "__main__":
    asyncio.run(main())
