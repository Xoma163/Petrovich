from apps.bot.classes.command import Command
from apps.bot.classes.const.consts import Role
from apps.bot.classes.const.exceptions import PWarning
from apps.bot.classes.help_text import HelpText, HelpTextItem
from apps.bot.classes.messages.response_message import ResponseMessage, ResponseMessageItem


class Settings(Command):
    name = "настройки"
    names = ["настройка"]
    name_tg = 'settings'

    help_text = HelpText(
        commands_text="устанавливает некоторые настройки пользователя/чата",
        help_texts=[
            HelpTextItem(Role.USER, [
                "- присылает текущие настройки",
                "упоминание (вкл/выкл) - определяет будет ли бот триггериться на команды без упоминания в конфе(требуются админские права)",
                "реагировать (вкл/выкл) - определяет, будет ли бот реагировать на неправильные команды в конфе. Это сделано для того, чтобы в конфе с несколькими ботами не было ложных срабатываний",
                "мемы (вкл/выкл) - определяет, будет ли бот присылать мем если прислано его точное название без / (боту требуется доступ к переписке)",
                "туретт (вкл/выкл) - определяет, будет ли бот случайно присылать ругательства",
                "голосовые (вкл/выкл) - определяет, будет ли бот автоматически распознавать голосовые",
                "др (вкл/выкл) - определяет, будет ли бот поздравлять с Днём рождения и будет ли ДР отображаться в /профиль",
                "ругаться (вкл/выкл) - определяет будет ли бот использовать ругательные команды",
            ]),
            HelpTextItem(Role.TRUSTED, [
                "gpt [конфа] (preprompt) - определяет system prompt для дальнейшего общения с ботом",
                "gpt [конфа] сбросить - сбрасывает system prompt"
            ]),
        ]
    )

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

    def start(self) -> ResponseMessage:
        if self.event.message.args:
            arg0 = self.event.message.args[0]
        else:
            arg0 = None

        menu = [
            [['реагировать', 'реагируй', 'реагирование'], self.menu_reaction],
            [['упоминание', 'упоминания', 'триггериться', 'тригериться'], self.menu_mentioning],
            [['мемы', 'мем'], self.menu_memes],
            [['др', 'днюха'], self.menu_bd],
            [['голосовые', 'голос', 'голосовухи', 'голосовуха', 'голосовое'], self.menu_voice],
            [['туретт', 'туррет', 'турретт', 'турет'], self.menu_turett],
            [['ругаться'], self.menu_swear],
            [['gpt', 'chatgpt'], self.menu_gpt],
            [['default'], self.menu_default],
        ]
        method = self.handle_menu(menu, arg0)
        rm = ResponseMessage(method())
        return rm

    def get_on_or_off(self, arg):
        if arg in self.ON_OFF_TRANSLATOR:
            return self.ON_OFF_TRANSLATOR[arg]
        else:
            raise PWarning("Не понял, включить или выключить?")

    def menu_reaction(self) -> ResponseMessageItem:
        return self.setup_default_chat_setting('need_reaction')

    def menu_mentioning(self) -> ResponseMessageItem:
        return self.setup_default_chat_setting('mentioning')

    def menu_memes(self) -> ResponseMessageItem:
        return self.setup_default_chat_setting('need_meme')

    def menu_bd(self) -> ResponseMessageItem:
        self.check_args(2)
        value = self.get_on_or_off(self.event.message.args[1])
        self.event.sender.celebrate_bday = value
        self.event.sender.save()
        answer = "Сохранил настройку"
        return ResponseMessageItem(text=answer)

    def menu_voice(self) -> ResponseMessageItem:
        return self.setup_default_chat_setting('recognize_voice')

    def menu_turett(self) -> ResponseMessageItem:
        return self.setup_default_chat_setting("need_turett")

    def menu_swear(self) -> ResponseMessageItem:
        return self.setup_default_chat_setting("use_swear")

    def menu_gpt(self) -> ResponseMessageItem:
        self.check_sender(Role.TRUSTED)
        self.check_args(2)
        if self.event.message.args[1] in ["чат", "конфа"]:
            self.check_conversation()
            self.check_args(3)
            if self.event.message.args[2] in ["сбросить", "удалить", "очистить"]:
                preprompt = ""
            else:
                preprompt = " ".join(self.event.message.args_case[2:])
            self.event.chat.gpt_preprompt = preprompt
            self.event.chat.save()
            save_for = "чата"
        else:
            if self.event.message.args[1] in ["сбросить", "удалить", "очистить"]:
                preprompt = ""
            else:
                preprompt = " ".join(self.event.message.args_case[1:])
            self.event.sender.gpt_preprompt = preprompt
            self.event.sender.save()
            save_for = "пользователя"

        if not preprompt:
            answer = f'Очистил GPT preprompt для {save_for}'
        else:
            answer = f'Сохранил GPT preprompt для {save_for}: "{preprompt}"'
        return ResponseMessageItem(text=answer)

    def menu_default(self) -> ResponseMessageItem:
        answer = ""
        if self.event.chat:
            answer = "Настройки чата:\n"

            reaction = self.event.chat.need_reaction
            need_meme = self.event.chat.need_meme
            mentioning = self.event.chat.mentioning
            turett = self.event.chat.need_turett
            recognize_voice = self.event.chat.recognize_voice
            use_swear = self.event.chat.use_swear

            answer += f"Реагировать на неправильные команды - {self.TRUE_FALSE_TRANSLATOR[reaction]}\n"
            answer += f"Присылать мемы по точным названиям - {self.TRUE_FALSE_TRANSLATOR[need_meme]}\n"
            answer += f"Триггериться на команды без упоминания - {self.TRUE_FALSE_TRANSLATOR[mentioning]}\n"
            answer += f"Автоматически распознавать голосовые - {self.TRUE_FALSE_TRANSLATOR[recognize_voice]}\n"
            answer += f"Синдром Туретта - {self.TRUE_FALSE_TRANSLATOR[turett]}\n"
            answer += f"Использовать ругательные команды - {self.TRUE_FALSE_TRANSLATOR[use_swear]}\n"

            if self.event.sender.check_role(Role.TRUSTED):
                answer += f"GPT preprompt - {self.bot.get_formatted_text_line(self.event.chat.gpt_preprompt)}\n"

            answer += "\n"

        answer += "Настройки пользователя:\n"

        celebrate_bday = self.event.sender.celebrate_bday
        answer += f"Поздравлять с днём рождения - {self.TRUE_FALSE_TRANSLATOR[celebrate_bday]}\n"
        if self.event.sender.check_role(Role.TRUSTED):
            answer += f"GPT preprompt - {self.bot.get_formatted_text_line(self.event.sender.gpt_preprompt)}\n"
        return ResponseMessageItem(text=answer)

    def setup_default_chat_setting(self, name) -> ResponseMessageItem:
        self.check_conversation()
        self.check_args(2)

        value = self.get_on_or_off(self.event.message.args[1])
        setattr(self.event.chat, name, value)
        self.event.chat.save()
        answer = "Сохранил настройку"
        return ResponseMessageItem(text=answer)
