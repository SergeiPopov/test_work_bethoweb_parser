class Command:
    def __init__(self, title: str, action):
        self.title = title
        self.action = action


class CmdListener:
    def __init__(self, commands_dict: dict[str, Command]):
        self.commands_dict = commands_dict

    async def listen(self):
        while True:
            self.print_all_commands()
            await self.parse_command()

    def print_all_commands(self):
        print("# КОМАНДЫ ПАРСЕРА #")
        for cmd, command_info in self.commands_dict.items():
            print(f"[{cmd}] {command_info.title}")

    async def parse_command(self):
        while True:
            user_command = input("Введите команду: ")
            if user_command and self.commands_dict.get(user_command):
                command = self.commands_dict.get(user_command)
                await command.action()
                print(f"Комманда '{command.title}' выполнена!")
                break
            print(f"Команды не существует или вы её не ввели")
