from apps.bot.classes.Command import Command
from apps.bot.classes.messages.ResponseMessage import ResponseMessage, ResponseMessageItem


class StartLada(Command):
    name = "заведи"
    names = ["завести"]

    def start(self) -> ResponseMessage:
        if self.event.message.args:
            who = self.event.message.args_str_case
            answer = ["уи ви ви ви ви ви ви ви", f'завожу {who}']
        else:
            answer = "уи ви ви ви ви ви ви ви"

        return ResponseMessage(ResponseMessageItem(text=answer))
