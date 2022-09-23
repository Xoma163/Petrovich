from apps.bot.classes.Command import Command
from apps.bot.classes.consts.Consts import Platform
from apps.bot.classes.consts.Exceptions import PWarning
from apps.bot.utils.utils import get_tg_formatted_text_line
from apps.service.models import Tag as TagModel


class Tag(Command):
    name = "тег"
    names = ["менш", "меншон", "вызов", "клич", "tag", "группа"]
    help_text = "тегает людей в конфе"
    help_texts = [
        "создать (название) - добавляет новую группу",
        "удалить (название) - удаляет новую группу",
        "добавить (название) (имя пользователя/никнейм) - добавляет пользователя в группу",
        "убрать (название) (имя пользователя/никнейм) - удаляет пользователя из группы",
        "список - выводит список всех тегов",
        "(название) - тегает всех пользователей в группе",
    ]
    conversation = True

    TAG_ALL = "all"

    @staticmethod
    def accept_extra(event):
        if event.message and not event.message.mentioned:
            if event.is_from_chat and event.message.command.startswith("@"):
                tag_name = event.message.command[1:]
                if tag_name == "all":
                    return True
                try:
                    TagModel.objects.get(name=tag_name, chat=event.chat)
                    return True
                except TagModel.DoesNotExist:
                    return False
        return False

    def start(self):
        if self.event.message.args:
            arg0 = self.event.message.args[0]
        else:
            arg0 = None

        menu = [
            [["создать", "create"], self.menu_create],
            [['удалить', "delete"], self.menu_delete],
            [["добавить", "add"], self.menu_add],
            [['убрать', "remove"], self.menu_remove],
            [['список', "list"], self.menu_list],
            [['default'], self.menu_default],
        ]
        method = self.handle_menu(menu, arg0)
        return method()

    def menu_create(self):
        self.check_args(2)
        name = self.event.message.args[1]
        if name == self.TAG_ALL:
            raise PWarning("Это имя зарезервировано для меншона всех участников конфы")
        try:
            tag = TagModel.objects.create(name=name, chat=self.event.chat)
        except Exception:  # Какой?
            raise PWarning(f"Тег \"{name}\" уже присутствует в этой конфе")

        return f"Тег \"{tag.name}\" создан"

    def menu_delete(self):
        self.check_args(2)
        tag = self._get_tag_by_name()
        tag.delete()

    def menu_add(self):
        self.check_args(2)
        tag = self._get_tag_by_name()

        profiles = []
        profiles_str = "".join(self.event.message.clear.split(' ')[3:]).split(',')
        for profile_str in profiles_str:
            profile = self.bot.get_profile_by_name(profile_str.split(' '), self.event.chat)
            profiles.append(profile)

        profiles = list(set(profiles))
        for profile in profiles:
            tag.users.add(profile)
        if len(profiles) == 1:
            return f"Пользователь {profiles[0]} добавлен в тег \"{tag.name}\""
        else:
            return f"Пользователи {', '.join(map(str, profiles))} добавлены в тег \"{tag.name}\""

    def menu_remove(self):
        self.check_args(2)
        tag = self._get_tag_by_name()

        profile_name = " ".join(self.event.message.args[2:])
        profile = self.bot.get_profile_by_name(profile_name, self.event.chat)

        tag.users.remove(profile)
        return f"Пользователь {profile} удалён из тега \"{tag.name}\""

    def _get_tag_name(self, name):
        if self.event.platform == Platform.TG:
            return get_tg_formatted_text_line(name)
        return name

    def menu_list(self):
        self.check_args(1)
        tags = TagModel.objects.filter(chat=self.event.chat)
        if not tags:
            return "Тегов нет"

        msg_list = [f"{self._get_tag_name(tag.name)}\n{', '.join([str(user) for user in tag.users.all()])}" for tag in
                    tags]
        return "\n\n".join(msg_list)

    def menu_default(self):
        if self.event.command and self.event.command == self:
            tag_name = self.event.message.command[1:]
        else:
            self.check_args(1)
            tag_name = self.event.message.args[0]

        if tag_name == self.TAG_ALL:
            users = self.event.chat.users.all().exclude(pk=self.event.sender.pk)
        else:
            tag = self._get_tag_by_name(tag_name)
            users = tag.users.exclude(pk=self.event.sender.pk)
        if not users:
            raise PWarning("В теге нет пользователей")
        msg_list = [self.bot.get_mention(user) for user in users]
        msg = "\n".join(msg_list)
        return msg

    def _get_tag_by_name(self, tag_name=None):
        if tag_name is None:
            tag_name = self.event.message.args[1]
        try:
            return TagModel.objects.get(name=tag_name, chat=self.event.chat)
        except TagModel.DoesNotExist:
            raise PWarning(f"Тега \"{tag_name}\" не существует")