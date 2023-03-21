from apps.bot.APIs.MinecraftAPI import get_minecraft_version_by_args
from apps.bot.APIs.TerrariaAPI import get_terraria_server_by_version
from apps.bot.classes.Command import Command
from apps.bot.classes.consts.Consts import Role


class Start(Command):
    name = "старт"

    help_text = "возобновляет работу сервиса"
    help_texts = ["(сервис) - майнкрафт/террария"]
    help_texts_extra = "Если майнкрафт, то может быть указана версия (1.12.2)"

    access = Role.TRUSTED
    args = 1

    def start(self):
        if self.event.message.args:
            arg0 = self.event.message.args[0]
        else:
            arg0 = None

        menu = [
            [["майн", "майнкрафт", "mine", "minecraft"], self.menu_minecraft],
            [['террария', 'terraria'], self.menu_terraria]
        ]
        method = self.handle_menu(menu, arg0)
        return method()

    def menu_minecraft(self):
        self.check_sender(Role.MINECRAFT)
        version = self.event.message.args[1] if len(self.event.message.args) > 1 else None
        minecraft_server = get_minecraft_version_by_args(version)
        version = minecraft_server.get_version()
        minecraft_server.event = self.event
        minecraft_server.start()

        message = f"Стартуем майн {version}"
        return message

    def menu_terraria(self):
        self.check_sender(Role.TERRARIA)
        terraria_server = get_terraria_server_by_version(None)
        terraria_server.start()
        return "Стартуем террарию!"
