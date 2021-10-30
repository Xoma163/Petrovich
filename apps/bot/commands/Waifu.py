from apps.bot.classes.Command import Command
from apps.bot.classes.consts.Consts import Platform
from apps.bot.classes.consts.Exceptions import PWarning
from apps.bot.utils.utils import get_random_int


class Waifu(Command):
    name = "вайфу"
    help_text = "присылает несуществующую вайфу"
    help_texts = [
        "[номер=рандом] - присылает несуществующую вайфу по номеру (0-100000)",
        "(слово) - присылает несуществующую вайфу вычисляя её номер"
    ]
    platforms = [Platform.VK, Platform.TG]

    def start(self):
        waifus_count = 100000
        if self.event.message.args:
            try:
                self.int_args = [0]
                self.parse_int()
                waifu_number = self.event.message.args[0]
                self.check_number_arg_range(waifu_number, 0, waifus_count)
            except PWarning:
                seed = self.event.message.args_str
                waifu_number = get_random_int(waifus_count, seed=seed)
        else:
            waifu_number = get_random_int(waifus_count)
        url = f"https://www.thiswaifudoesnotexist.net/example-{waifu_number}.jpg"
        attachment = self.bot.upload_photos(url, peer_id=self.event.peer_id)

        if self.event.message.args:

            keyboard = self.bot.get_inline_keyboard(
                [{'command': self.name, 'button_text': "Следующая", 'args': [waifu_number+1]}])
        else:
            keyboard = self.bot.get_inline_keyboard([{'command': self.name, 'button_text': "Ещё"}])
        return {"text": waifu_number, "attachments": attachment, "keyboard": keyboard}
