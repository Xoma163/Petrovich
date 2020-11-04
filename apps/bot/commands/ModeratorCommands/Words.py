from apps.bot.classes.Consts import Role
from apps.bot.classes.common.CommonCommand import CommonCommand
from apps.service.management.commands.get_words import Command


class Words(CommonCommand):
    def __init__(self):
        names = ["слова"]
        help_text = "Слова - принудительно затягивает слова с Google Drive"
        super().__init__(names, help_text, access=Role.MODERATOR)

    def start(self):
        get_words = Command()
        return get_words.handle()
