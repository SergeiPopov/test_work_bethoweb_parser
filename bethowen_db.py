import asyncio
import logging
from typing import List

from bethowen_parser import BHParser
from sql_connector import SQLiteConnector
import migrations


class BHDb:
    def __init__(self, parser: BHParser, db_name: str = "parser.db"):
        self.sql_con = SQLiteConnector(db_name)
        self.parser = parser

    async def init_db(self):
        self.migrate()
        await self.init_categories()
        await self.init_shops()
        logging.info("База данных инициализирована")

    async def init_categories(self):
        exist_categories = self.get_categories()
        if not exist_categories:
            categories = await self.parser.get_categories()
            self.insert_categories(categories)

    async def init_shops(self):
        exist_shops = self.get_shops()
        if not exist_shops:
            shops = await self.parser.get_shops()
            self.insert_shops(shops)

    def migrate(self):
        for module_var in dir(migrations):
            if 'sql' in module_var:
                raw_sql = getattr(migrations, module_var)
                self.sql_con.execute(raw_sql)


    def get_products(self, hash_parse: int, limit=10, offset=0):
        return self.sql_con.execute("""SELECT * FROM Parse 
                                               WHERE parse_hash = ? 
                                               LIMIT ? OFFSET ?""", (hash_parse, limit, offset)).fetchall()



    def get_shop_by_id(self, shop_id: int):
        return self.sql_con.execute("""SELECT * FROM Shops WHERE shop_id = ?""", (shop_id, )).fetchone()

    def get_shops(self) -> List[tuple]:
        return self.sql_con.execute("""SELECT * FROM Shops""").fetchall()

    def insert_shops(self, shops: List[tuple]):
        for shop in shops:
            self.sql_con.execute("INSERT INTO Shops "
                                 "(shop_id, shop_url, shop_addr, shop_tel)"
                                 " VALUES (?, ?, ?, ?)", shop)

    def get_categories(self) -> List[tuple]:
        return self.sql_con.execute("""SELECT * FROM Categories""").fetchall()

    def insert_categories(self, categories: List[tuple]):
        for cat in categories:
            self.sql_con.execute("INSERT INTO Categories (cat_url, cat_title) VALUES (?, ?)", cat)

    def get_config(self) -> tuple:
        return self.sql_con.execute("""SELECT * FROM ParserConfig""").fetchone()

    def insert_config(self, config: tuple):
        self.sql_con.execute("DELETE from ParserConfig")
        self.sql_con.execute("INSERT INTO ParserConfig "
                             "(town_id, town_name, shop_id) "
                             "VALUES (?, ?, ?)", config)

    def get_last_parse_hash(self) -> int:
        parse_hash = self.sql_con.execute("SELECT MAX(parse_hash) FROM Parse").fetchone()
        if not parse_hash[0]:
            return 0
        return parse_hash[0]

    def insert_product(self, parse_hash: int, products: tuple):
        self.sql_con.execute("INSERT INTO Parse "
                             "(parse_hash,"
                             "product_id,"
                             "product_url,"
                             "product_name,"
                             "product_size,"
                             "product_vendor_code,"
                             "product_discount_price,"
                             "product_retail_price,"
                             "shop_availability) "
                             "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                             (parse_hash, *products))

    async def close(self):
        self.sql_con.close()
        await self.parser.close()


async def main():
    logging.basicConfig(level=logging.INFO)
    parser = BHParser()
    db = BHDb(parser)
    await db.init_db()
    print(db.get_shop_by_id(10))
    await db.close()


if __name__ == "__main__":
    asyncio.run(main())