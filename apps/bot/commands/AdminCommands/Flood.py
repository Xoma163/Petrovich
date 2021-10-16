from apps.bot.classes.Command import Command
from apps.bot.classes.consts.Consts import Role, Platform


class Flood(Command):
    name = "флуд"
    help_text = "флудит"
    help_texts = ["(N) - флудит N сообщений"]
    access = Role.ADMIN
    args = 1
    int_args = [0]
    platforms = [Platform.VK, Platform.TG]

    def start(self):
        text = "ыыыыыыыыыыыыыыыыыыыыыыыыыыыыыыыыыыыыыы"
        count = self.event.message.args[0]
        msgs = [{'text': text}] * count
        return msgs
