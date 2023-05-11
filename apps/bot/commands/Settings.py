from django.contrib.auth.models import Group

from apps.bot.classes.Command import Command
from apps.bot.classes.consts.Consts import Role
from apps.bot.classes.consts.Exceptions import PWarning


class Settings(Command):
    name = "настройки"
    names = ["настройка"]
    name_tg = 'settings'

    help_text = "устанавливает некоторые настройки пользователя/чата"
    help_texts = [
        "- присылает текущие настройки",
        "упоминание (вкл/выкл) - определяет будет ли бот триггериться на команды без упоминания в конфе(требуются админские права)",
        "реагировать (вкл/выкл) - определяет, будет ли бот реагировать на неправильные команды в конфе. Это сделано для того, чтобы в конфе с несколькими ботами не было ложных срабатываний",
        "мемы (вкл/выкл) - определяет, будет ли бот присылать мем если прислано его точное название без / (боту требуется доступ к переписке)",
        "туретт (вкл/выкл) - определяет, будет ли бот случайно присылать ругательства",
        "голосовые (вкл/выкл) - определяет, будет ли бот автоматически распознавать голосовые",
        "майнкрафт (вкл/выкл) - определяет, будет ли бот присылать информацию о серверах майна. (для доверенных)",
        "др (вкл/выкл) - определяет, будет ли бот поздравлять с Днём рождения и будет ли ДР отображаться в /профиль",
        "ругаться (вкл/выкл) - определяет будет ли бот использовать ругательные команды"
    ]

    ON_OFF_TRANSLATOR = {
        'вкл': True,
        'on': True,
        '1': True,
        'true': True,
        'включить': True,
        'включи': True,
        'вруби': True,
        'подключи': True,
        'истина': True,

        'выкл': False,
        'off': False,
        '0': False,
        'false': False,
        'выключить': False,
        'выключи': False,
        'выруби': False,
        'отключи': False,
        'ложь': False
    }

    TRUE_FALSE_TRANSLATOR = {
        True: 'вкл ✅',
        False: 'выкл ⛔'
    }

    def start(self):
        if self.event.message.args:
            arg0 = self.event.message.args[0]
        else:
            arg0 = None

        menu = [
            [['реагировать', 'реагируй', 'реагирование'], self.menu_reaction],
            [['упоминание', 'упоминания', 'триггериться', 'тригериться'], self.menu_mentioning],
            [['майнкрафт', 'майн', 'minecraft', 'mine'], self.menu_minecraft_notify],
            [['мемы', 'мем'], self.menu_memes],
            [['др', 'днюха'], self.menu_bd],
            [['голосовые', 'голос', 'голосовухи', 'голосовуха', 'голосовое'], self.menu_voice],
            [['туретт', 'туррет', 'турретт', 'турет'], self.menu_turett],
            [['ругаться'], self.menu_swear],
            [['default'], self.menu_default],
        ]
        method = self.handle_menu(menu, arg0)
        return method()

    def get_on_or_off(self, arg):
        if arg in self.ON_OFF_TRANSLATOR:
            return self.ON_OFF_TRANSLATOR[arg]
        else:
            raise PWarning("Не понял, включить или выключить?")

    def menu_reaction(self):
        return self.setup_default_chat_setting('need_reaction')

    def menu_mentioning(self):
        return self.setup_default_chat_setting('mentioning')

    def menu_memes(self):
        return self.setup_default_chat_setting('need_meme')

    def menu_bd(self):
        self.check_args(2)
        value = self.get_on_or_off(self.event.message.args[1])
        self.event.sender.celebrate_bday = value
        self.event.sender.save()
        return "Сохранил настройку"

    def menu_minecraft_notify(self):
        self.check_sender(Role.TRUSTED)
        self.check_args(2)

        value = self.get_on_or_off(self.event.message.args[1])

        group_minecraft_notify = Group.objects.get(name=Role.MINECRAFT_NOTIFY.name)
        if value:
            self.event.sender.groups.add(group_minecraft_notify)
            self.event.sender.save()
            return "Подписал на рассылку о сервере майна"
        else:
            self.event.sender.groups.remove(group_minecraft_notify)
            self.event.sender.save()
            return "Отписал от рассылки о сервере майна"

    def menu_voice(self):
        return self.setup_default_chat_setting('recognize_voice')

    def menu_turett(self):
        return self.setup_default_chat_setting("need_turett")

    def menu_swear(self):
        return self.setup_default_chat_setting("use_swear")

    def menu_default(self):
        msg = ""
        if self.event.chat:
            msg = "Настройки чата:\n"

            reaction = self.event.chat.need_reaction
            need_meme = self.event.chat.need_meme
            mentioning = self.event.chat.mentioning
            turett = self.event.chat.need_turett
            recognize_voice = self.event.chat.recognize_voice
            use_swear = self.event.chat.use_swear

            msg += f"Реагировать на неправильные команды - {self.TRUE_FALSE_TRANSLATOR[reaction]}\n"
            msg += f"Присылать мемы по точным названиям - {self.TRUE_FALSE_TRANSLATOR[need_meme]}\n"
            msg += f"Триггериться на команды без упоминания - {self.TRUE_FALSE_TRANSLATOR[mentioning]}\n"
            msg += f"Автоматически распознавать голосовые - {self.TRUE_FALSE_TRANSLATOR[recognize_voice]}\n"
            msg += f"Синдром Туретта - {self.TRUE_FALSE_TRANSLATOR[turett]}\n"
            msg += f"Использовать ругательные команды - {self.TRUE_FALSE_TRANSLATOR[use_swear]}\n"

            msg += "\n"

        msg += "Настройки пользователя:\n"

        if self.event.sender.check_role(Role.TRUSTED):
            minecraft_notify = self.event.sender.check_role(Role.MINECRAFT_NOTIFY)
            msg += f"Уведомления по майну - {self.TRUE_FALSE_TRANSLATOR[minecraft_notify]}\n"
        celebrate_bday = self.event.sender.celebrate_bday
        msg += f"Поздравлять с днём рождения - {self.TRUE_FALSE_TRANSLATOR[celebrate_bday]}\n"
        return msg

    def setup_default_chat_setting(self, name):
        self.check_conversation()
        self.check_sender(Role.CONFERENCE_ADMIN)
        self.check_args(2)

        value = self.get_on_or_off(self.event.message.args[1])
        setattr(self.event.chat, name, value)
        self.event.chat.save()
        return "Сохранил настройку"
