import asyncio

from bethowen_db import BHDb
from bethowen_parser import BHParser

class BHCsv:
    def __init__(self, parser: BHParser, db: BHDb):
        self.parser = parser
        self.db = db

    async def get_csv_by_hash_parse(self):
        hash_parse = input("Введите hash парсинга: ")
        if hash_parse.isnumeric():
            await self.write_to_csv_file(f'{hash_parse}_parse.csv', int(hash_parse))
        else:
            print("Вы ввели некоректный hash парсинга")

    async def get_csv_by_last_parse(self):
        last_hash_parse = self.db.get_last_parse_hash()
        await self.write_to_csv_file(f"{last_hash_parse}_last_parse.csv", last_hash_parse)

    async def write_to_csv_file(self, csv_name: str, hash_parse: int):
        with open(csv_name, 'w', encoding='utf8') as file:
            is_empty = False
            limit = 10
            i = 1
            while not is_empty:
                products = self.db.get_products(hash_parse, limit, limit*(i-1))
                if not products:
                    is_empty = True
                else:
                    for p in products:
                        file.write(",".join(list(map(str,p))) + '\n')
                i += 1

async def main():
    parser = BHParser()
    db = BHDb(parser)
    bh_csv = BHCsv(parser, db)
    bh_csv.get_csv_by_hash_parse()


if __name__ == "__main__":
    asyncio.run(main())

