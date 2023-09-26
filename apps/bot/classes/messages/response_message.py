import re
from copy import copy
from typing import List


class ResponseMessageItem:
    TG_TAGS = ['pre', 'code', 'i', 'b', 'u']

    def __init__(
            self, text: str = None, attachments: list = None, reply_to: str = None, keyboard: dict = None,
            message_id: str = None, message_thread_id: str = None, peer_id: int = None, log_level='debug', exc_info=None
    ):
        self.text = text
        self.attachments = attachments if attachments else []
        if not isinstance(self.attachments, list):
            self.attachments = [self.attachments]
        self.reply_to = reply_to
        self.keyboard = keyboard
        self.message_id = message_id
        self.message_thread_id = message_thread_id
        self.peer_id = peer_id

        self.log_level = log_level
        self.exc_info = exc_info

        self.kwargs = {}

    def to_log(self) -> dict:
        """
        Вывод в логи
        """
        dict_self = copy(self.__dict__)
        ignore_fields = ['log_level', 'exc_info']
        for ignore_field in ignore_fields:
            del dict_self[ignore_field]

        dict_self["attachments"] = [x.to_log() for x in dict_self["attachments"]]
        return dict_self

    def to_api(self) -> dict:
        """
        Вывод в API
        """
        dict_self = copy(self.__dict__)

        ignore_fields = ['log_level', 'exc_info', "peer_id"]
        for ignore_field in ignore_fields:
            del dict_self[ignore_field]
        dict_self["attachments"] = [x.to_api() for x in dict_self["attachments"]]

        return dict_self

    def set_telegram_html(self):
        urls_regexp = r"(http|ftp|https|tg)(:\/\/)([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])"
        if self.text:
            p = re.compile(urls_regexp)  # Ссылки
            if p.search(self.text):
                self.kwargs = {'parse_mode': "html"}
            else:
                for tag in self.TG_TAGS:
                    p = re.compile(f"<{tag}>[\s\S]*</{tag}>")
                    if p.search(self.text):
                        self.kwargs = {'parse_mode': "html"}
                        break

            if self.kwargs.get('parse_mode'):
                # Врапим ссылки без явного их врапа если у нас уже html
                url_poss = re.finditer(urls_regexp, self.text)  # Ссылки не в скобках
                url_poss = reversed(list(url_poss))  # Заменяем всё в строке с конца, чтобы были корректные позиции
                for url_pos in url_poss:
                    start_pos = url_pos.start()
                    end_pos = url_pos.end()

                    url = self.text[start_pos:end_pos]

                    # Если ссылка уже враплена, то продолжаем просто дальше
                    left_part = None
                    right_part = None
                    if start_pos >= 9:
                        left_part = self.text[start_pos - 9:start_pos]
                    if len(self.text) > end_pos:
                        right_part = self.text[end_pos:end_pos + 2]
                    if left_part == '<a href="' and right_part == '">':
                        continue

                    if len(self.attachments) < 2:
                        from apps.bot.classes.bots.tg_bot import TgBot
                        self.text = self.text[:start_pos] + TgBot.get_formatted_url(url, url) + self.text[end_pos:]

    def __str__(self):
        return self.text if self.text else ""


class ResponseMessage:
    def __init__(self, messages=None):
        if messages is None:
            messages = []
        if isinstance(messages, list):
            self.messages: List[ResponseMessageItem] = messages
        else:
            self.messages: List[ResponseMessageItem] = [messages]

    def to_log(self) -> dict:
        """
        Вывод в логи
        """
        dict_self = copy(self.__dict__)
        dict_self["messages"] = [x.to_log() for x in dict_self["messages"]]
        return dict_self

    def to_api(self) -> dict:
        """
        Вывод в API
        """
        dict_self = copy(self.__dict__)
        dict_self["messages"] = [x.to_api() for x in dict_self["messages"]]

        return dict_self

    def __bool__(self):
        return len(self.messages) > 0