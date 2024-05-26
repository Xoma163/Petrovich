from collections import OrderedDict
from itertools import groupby

from apps.bot.classes.bots.chat_activity import ChatActivity
from apps.bot.classes.command import Command
from apps.bot.classes.const.activities import ActivitiesEnum
from apps.bot.classes.const.consts import Role, Platform
from apps.bot.classes.const.exceptions import PWarning
from apps.bot.classes.event.event import Event
from apps.bot.classes.event.tg_event import TgEvent
from apps.bot.classes.help_text import HelpTextItemCommand
from apps.bot.classes.messages.response_message import ResponseMessage
from apps.bot.utils.cache import MessagesCache


class WTFCommand(Command):
    name = "wtf"
    names = ['саммари', 'суммаризируй']
    access = Role.TRUSTED
    abstract = True
    platforms = [Platform.TG]

    DEFAULT_PROMPT = "Я пришлю тебе переписку участников группы. Суммаризируй её, опиши, что произошло, о чём общались люди?"
    DEFAULT_N = 50
    DEFAULT_HELP_TEXT_ITEMS = [
        HelpTextItemCommand(
            f"[prompt] [N={DEFAULT_N}]",
            "обрабатывает последние N сообщений в конфе через ChatGPT по указанному prompt"
        ),
        HelpTextItemCommand(
            "(пересланное сообщение)",
            "обрабатывает последние сообщения до пересланного в конфе через ChatGPT по указанному prompt"
        )
    ]

    GPT_COMMAND_CLASS = None

    def start(self) -> ResponseMessage:
        n, prompt = self._get_n_and_prompt()

        with ChatActivity(self.bot, ActivitiesEnum.TYPING, self.event.peer_id):
            messages = self.get_conversation(n, prompt)

        gpt = self.GPT_COMMAND_CLASS()
        gpt.bot = self.bot
        gpt.event = self.event

        with ChatActivity(self.bot, ActivitiesEnum.TYPING, self.event.peer_id):
            answer = gpt.completions(messages)
        return ResponseMessage(answer)

    def _get_n_and_prompt(self) -> tuple[int, str]:
        try:
            self.check_fwd()
            last_message_id = self.event.fwd[0].message.id
            current_message_id = self.event.message.id
            n = current_message_id - last_message_id
            prompt = self.event.message.args_str_case
        except PWarning:
            try:
                last_arg = self.event.message.args[-1]
                n = int(last_arg)
                prompt = " ".join(self.event.message.args_case[:-1])
            except (ValueError, IndexError):
                n = self.DEFAULT_N
                prompt = self.event.message.args_str_case

        if not prompt:
            prompt = self.DEFAULT_PROMPT
        return n, prompt

    @staticmethod
    def _format_groupped_messages(last_user, messages_from_one_user):
        message_header = f"[{last_user.name}]"
        message_body = "\n".join(messages_from_one_user)
        message = f"{message_header}\n{message_body}"
        return message

    def get_conversation(self, n: int, prompt: str) -> list:
        events = self.get_last_messages_as_events(n)
        result_message = []

        events = list(filter(lambda x: x.is_from_user and x.message.raw, events))
        for sender, events in groupby(events, key=lambda x: x.sender):
            messages_from_one_user = []
            for event in events:
                messages_from_one_user.append(event.message.raw)
            message = self._format_groupped_messages(sender, messages_from_one_user)
            result_message.append(message)

        messages = []
        preprompt = self.GPT_COMMAND_CLASS.get_preprompt(
            self.event.sender,
            self.event.chat,
            self.GPT_COMMAND_CLASS.PREPROMPT_PROVIDER
        )
        if preprompt:
            messages.append({"role": "system", "content": preprompt})
        messages.append({'role': "user", 'content': prompt})
        messages.append({'role': "user", 'content': "\n".join(result_message)})
        return messages

    def get_last_messages_as_events(self, n: int) -> list[Event]:
        mid = self.event.message.id
        peer_id = self.event.peer_id

        mc = MessagesCache(peer_id)
        data = mc.get_messages()
        messages = OrderedDict(sorted(data.items(), key=lambda x: x[0], reverse=True))
        events = []

        for message_id, message_body in messages.items():
            # не берём последнее сообщение, которым зашли в эту команду :)
            if 1 <= mid - message_id < n + 1:
                try:
                    event = TgEvent({'message': message_body})
                    event.setup_event()
                except Exception:
                    continue
                events.append(event)
        events = list(reversed(events))

        return events