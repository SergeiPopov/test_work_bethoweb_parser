import logging
import re
import asyncio
from typing import Union

from bethowen_parser import BHParser
from bethowen_db import BHDb


class BHParserConfig:
    def __init__(self, parser: BHParser, db: BHDb):
        self.town_id = None
        self.town_name = None
        self.shop_id = None
        self.db = db
        self.parser = parser

    def __repr__(self):
        return (f"Конфиг парсера: \n"
                f"Город - {self.town_name};\n"
                f"Магазин - {self.db.get_shop_by_id(self.shop_id)[2]}")

    async def init_config(self):
        config_from_db = self.get_config()
        if config_from_db:
            self.town_id, self.town_name, self.shop_id = config_from_db
        else:
            await self.set_config()
        logging.info(f"Конфигурация парсера инициализирована город - {self.town_name}, номер ТТ на сайте - {self.shop_id}")

    def get_config(self) -> Union[tuple, None]:
        config_from_db = self.db.get_config()
        if config_from_db:
            return config_from_db

    async def set_config(self):
        self.town_id, self.town_name = await self.set_tower()
        self.shop_id = await self.set_shop()
        self.db.insert_config((self.town_id,
                               self.town_name,
                               self.shop_id))

    async def set_tower(self) -> tuple[int, str]:
        while True:
            town_term = input("Введите название города: ")
            possible_towns = await self.parser.get_town(town_term)
            if not possible_towns:
                print("Нет подходящего города")
                continue
            for i, pos_town in enumerate(possible_towns):
                print(f'[{i}]', pos_town.get('name'), ' | ', pos_town.get('description'))
            town_num = input("Выберите подходящий город по номеру: ")
            if town_num.isnumeric() and 0 <= int(town_num) <= len(possible_towns) - 1:
                town = possible_towns[int(town_num)]
                print(f"Вы выбрали город {town['name']}")
                return int(town['id']), town['name'] + " | " + town['description']
            print("Вы выбрали несуществующий номер города")

    async def set_shop(self) -> int:
        possible_shops = await self.parser.get_shops()
        while True:
            for i, pos_shop in enumerate(possible_shops):
                print(f'[{i}]', pos_shop[2], ' | ', pos_shop[3])
            shop_num = input("Выберите магазин: ")
            if shop_num.isnumeric() and 0 <= int(shop_num) <= len(possible_shops)-1:
                shop = possible_shops[int(shop_num)]
                shop_id = int(re.search(r'\d+', shop[1]).group())
                print(f"Вы выбрали магазин {shop[2]}")
                return shop_id
            print("Вы выбрали несуществующий номер магазина")


async def main():
    logging.basicConfig(level=logging.INFO)
    parser = BHParser()
    db = BHDb()
    config = BHParserConfig(parser, db)
    await config.init_config()

if __name__ == "__main__":
    asyncio.run(main())

