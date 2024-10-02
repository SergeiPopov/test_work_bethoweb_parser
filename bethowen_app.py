from command_listener import Command, CmdListener
from bethowen_controller import BHController


class BHApp:
    def __init__(self):
        self.controller = BHController()
        self.command_dict = {
            'getcfg': Command('Просмотреть настройки парсера', action=self.controller.command_get_config),
            'setcfg': Command('Настроить парсер', action=self.controller.config.set_config),
            'cats': Command('Спарсить все товары', action=self.controller.command_get_all_products),
            'cat': Command("Спарсить товары категории", action=self.controller.command_get_product_by_category),
            'catpage': Command("Спарсить товары категории со страницы", action=self.controller.command_get_products_by_category_and_page),
            'csvlast': Command("CSV файл с последними полученными товарами", action=self.controller.command_get_csv_last_parse),
            'csvhash': Command("CSV файл с конкретным hash парсингом", action=self.controller.command_get_csv_by_hash_parse),
            'exit': Command('Закрыть парсер', action=self.end)
        }
        self.cmd_listener = CmdListener(self.command_dict)

    async def start(self):
        await self.controller.init_controller()
        await self.cmd_listener.listen()

    async def end(self):
        await self.controller.close()
        exit(0)
