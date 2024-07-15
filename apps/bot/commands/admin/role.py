from apps.bot.classes.bots.tg_bot import TgBot
from apps.bot.classes.command import Command
from apps.bot.classes.const.consts import Role
from apps.bot.classes.const.exceptions import PWarning
from apps.bot.classes.help_text import HelpText, HelpTextItem, HelpTextItemCommand
from apps.bot.classes.messages.response_message import ResponseMessage, ResponseMessageItem
from apps.bot.models import Profile
from apps.bot.utils.utils import get_role_by_str


class Roles(Command):
    name = "роль"
    names = ["роли"]
    access = Role.ADMIN
    help_text = HelpText(
        commands_text="добавление и удаление ролей пользователю",
        help_texts=[
            HelpTextItem(Role.ADMIN, [
                HelpTextItemCommand("добавить (пользователь) (роль)", "добавляет роль пользователю"),
                HelpTextItemCommand("удалить (пользователь) (роль)", "удаляет роль пользователю")
            ])
        ]
    )
    conversation = True
    args = 3

    bot: TgBot

    def start(self) -> ResponseMessage:
        action, username, role_str = self.event.message.args_str.split(' ', 3)
        profile = self.bot.get_profile_by_name([username], self.event.chat)
        role = get_role_by_str(role_str)
        if role in [Role.ADMIN, Role.BANNED, Role.USER]:
            raise PWarning(f"Нельзя добавлять/удалять роль \"{role}\"")

        if action == "добавить":
            rmi = self.add_role(profile, role)
        elif action == "удалить":
            rmi = self.remove_role(profile, role)
        else:
            raise PWarning(f"Неизвестное действие - \"{action}\"")
        return ResponseMessage(rmi)

    @staticmethod
    def add_role(profile: Profile, role: Role) -> ResponseMessageItem:
        if profile.check_role(role):
            raise PWarning(f"У пользователя уже есть роль \"{role}\"")
        profile.add_role(role)
        return ResponseMessageItem(f"Добавил пользователю \"{profile}\" роль \"{role}\"")

    @staticmethod
    def remove_role(profile: Profile, role: Role) -> ResponseMessageItem:
        if profile.check_role(role):
            raise PWarning(f"У пользователя нет роли \"{role}\"")
        profile.remove_role(role)
        return ResponseMessageItem(f"Удалил пользователю \"{profile}\" роль \"{role}\"")
