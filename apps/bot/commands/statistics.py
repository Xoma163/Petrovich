import datetime

from django.db.models import Count, Q, QuerySet

from apps.bot.classes.command import Command
from apps.bot.classes.const.consts import Role
from apps.bot.classes.const.exceptions import PWarning
from apps.bot.classes.help_text import HelpText, HelpTextItem, HelpTextItemCommand
from apps.bot.classes.messages.response_message import ResponseMessage, ResponseMessageItem
from apps.bot.models import Profile
from apps.games.models import Gamer
from apps.games.models import PetrovichUser
from apps.service.models import Meme


class Statistics(Command):
    name = "статистика"
    names = ["стата"]

    help_text = HelpText(
        commands_text="статистика по победителям игр или по кол-ву созданных мемов",
        help_texts=[
            HelpTextItem(Role.USER, [
                HelpTextItemCommand("[модуль=все]", "статистика по победителям игр или по кол-ву созданных мемов"),
                HelpTextItemCommand("(петрович) [год=текущий]", "статистика по победителям петровича")
            ])
        ],
        extra_text=(
            "Модули: петрович, мемы, \n"
            "Если выбран модуль петрович и передан ключ --all, то выведутся пользователи которые также покинули группу"
        ),
    )

    def start(self) -> ResponseMessage:
        if not self.event.message.args:
            answer = self.menu_all()
        else:
            arg0 = self.event.message.args[0]
            menu = [
                [['петрович'], self.menu_petrovich],
                [['wordle', 'вордле'], self.menu_wordle],
                [['мемы'], self.menu_memes],
            ]
            method = self.handle_menu(menu, arg0)
            answer = method()
        return ResponseMessage(ResponseMessageItem(text=answer))

    def menu_petrovich(self) -> str:
        self.check_conversation()

        if len(self.event.message.args) > 1:
            self.int_args = [1]
            self.parse_int()
            year = self.event.message.args[1]
        else:
            year = datetime.datetime.now().year

        if self.event.message.keys and "all" in self.event.message.keys:
            players = PetrovichUser.objects.filter(chat=self.event.chat)
        else:
            players = PetrovichUser.objects.filter(chat=self.event.chat, profile__chats=self.event.chat)

        players = sorted(players, key=lambda t: t.wins_by_year(year), reverse=True)

        players_list = [player for player in players if player.wins_by_year(year)]
        msg = "Наши любимые Петровичи:\n"
        if len(players_list) == 0:
            return msg + f"Нет статистики за {year} год"

        players_list_str = "\n".join([f"{player} - {player.wins_by_year(year)}" for player in players_list])
        return msg + players_list_str

    def menu_wordle(self) -> str:
        return self._get_str_game_stat("wordle_points", "Побед Wordle")

    def menu_memes(self) -> str:
        if self.event.is_from_chat:
            profiles = Profile.objects.filter(chats=self.event.chat)
        else:
            profiles = Profile.objects.filter(pk=self.event.sender.pk)

        result_list = Meme.objects.filter(author__in=profiles) \
            .values('author') \
            .annotate(total=Count('author')) \
            .order_by('-total')

        msg = "Созданных мемов:"
        if self.event.is_from_pm:
            return f"{msg} {result_list[0]['total']}"

        if result_list.count() == 0:
            raise PWarning(f"{msg}\nНет статистики")
        result_list_str = "\n".join([f"{profiles.get(id=x['author'])} - {x['total']}" for x in result_list])
        return f"{msg}\n{result_list_str}"

    def menu_all(self):
        methods = [
            self.menu_petrovich,
            self.menu_wordle,
            self.menu_memes,
        ]
        answer = ""
        for val in methods:
            try:
                answer += f"{val()}\n\n"
            except PWarning:
                continue
        return answer

    def _get_gamers(self, exclude, order_by) -> QuerySet:
        if self.event.is_from_chat:
            return Gamer.objects.filter(profile__chats=self.event.chat).exclude(exclude).order_by(order_by)
        else:
            return Gamer.objects.filter(pk=self.event.sender.gamer.pk).exclude(exclude)

    def _get_str_game_stat(self, field: str, win_in_str: str):
        gamers = self._get_gamers(exclude=Q(**{field: 0}), order_by=f"-{field}")
        if gamers.count() == 0:
            raise PWarning()

        msg = f"{win_in_str}:"
        if self.event.is_from_pm:
            return f"{msg} {getattr(gamers[0], field)}"

        if gamers.count() == 0:
            raise PWarning(msg + "Нет статистики")
        gamers_str = "\n".join([f"{gamer} - {getattr(gamer, field)}" for gamer in gamers])
        return f"{msg}\n{gamers_str}"
