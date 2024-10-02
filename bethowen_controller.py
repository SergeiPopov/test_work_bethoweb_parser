import asyncio
import logging

from bethowen_parser import BHParser
from bethowen_db import BHDb
from bethowen_config import BHParserConfig
from bethowen_csv import BHCsv


class BHController:
    def __init__(self):
        self.parser = BHParser()
        self.db = BHDb(self.parser)
        self.config = BHParserConfig(self.parser, self.db)
        self.bh_csv = BHCsv(self.parser, self.db)

    async def init_controller(self):
        await self.config.init_config()
        await self.db.init_db()

    def select_category_for_parsing(self) -> tuple:
        categories = self.db.get_categories()
        for i, cat in enumerate(categories):
            print(f"[{i}] Категория {cat[2]} по ссылке {self.parser.base_url + cat[1]}")

        selected_cat = None
        while not selected_cat:
            cat_num = input("Выберите категорию товаров: ")
            if cat_num.isnumeric() and 0 <= int(cat_num) <= len(categories) - 1:
                selected_cat = categories[int(cat_num)]
                print(f"Вы выбрали категорию {selected_cat[2]}")
                return selected_cat
            print("Вы ввели несуществующую категорию")

    async def select_page_for_parsing(self, url) -> int:
        pages = await self.parser.get_max_page_in_category(url)
        selected_page = None
        while not selected_page:
            user_page = input(f"Выберите страницу для парсинга одну из {pages} страниц: ")
            if user_page.isnumeric() and pages >= int(user_page):
                selected_page = int(user_page)
        return selected_page

    async def command_get_products_by_category_and_page(self):
        parse_hash = self.get_new_parse_hash()
        selected_cat = self.select_category_for_parsing()
        selected_page = await self.select_page_for_parsing(self.parser.base_url + selected_cat[1])
        await self.get_products_by_category_and_page(parse_hash, self.parser.base_url + selected_cat[1], selected_page)

    async def command_get_product_by_category(self):
        selected_cat = self.select_category_for_parsing()
        parse_hash = self.get_new_parse_hash()
        await self.get_products_by_category(parse_hash, self.parser.base_url + selected_cat[1])

    async def command_get_all_products(self):
        parse_hash = self.get_new_parse_hash()
        categories = self.db.get_categories()
        for category in categories:
            url = self.parser.base_url + category[1]
            await self.get_products_by_category(parse_hash, url)

    async def command_get_config(self):
        print(self.config)

    async def command_get_csv_last_parse(self):
        await self.bh_csv.get_csv_by_last_parse()

    async def command_get_csv_by_hash_parse(self):
        await self.bh_csv.get_csv_by_hash_parse()

    async def get_products_by_category(self, parse_hash: int, url: str):
        pages =  await self.parser.get_max_page_in_category(url)
        for p in range(1, pages+1):
            await self.get_products_by_category_and_page(parse_hash, url, p)

    async def get_products_by_category_and_page(self, parse_hash: int, url: str, page: int):
        products = await self.parser.get_products_in_category(url, page)
        for prod in products:
            available_shops = prod[-1]['offer_store_amount']
            shop_info = None
            for shop in available_shops:
                if int(shop.get('shop_id')) == self.config.shop_id:
                    shop_info = "Кол-во товаров: " + shop['availability']['text'].upper() + f' на {shop['address'][:30]}...'
                    break
            if shop_info:
                product_for_db = (*prod[:-1], shop_info)
                self.db.insert_product(parse_hash, product_for_db)
        logging.info(f"Парсинг {page} страницы категори {url} прошел успешно! hash парсинга - {parse_hash}")

    def get_new_parse_hash(self):
        new_parse_hash = self.db.get_last_parse_hash() + 1
        logging.info(f"Текущий hash парсинга {new_parse_hash}")
        return new_parse_hash

    async def close(self):
        await self.parser.close()
        await self.db.close()


async def main():
    logging.basicConfig(level=logging.INFO)
    bh_controller = BHController()
    await bh_controller.init_controller()
    await bh_controller.command_get_products_by_category_and_page()
    await bh_controller.close()

if __name__ == "__main__":
    asyncio.run(main())