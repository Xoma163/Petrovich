import threading
from datetime import datetime

from django.core.management import call_command
from django.core.management.base import BaseCommand

from apps.bot.utils.utils import localize_datetime
from crontab import CronTab
from petrovich.settings import TIME_ZONE


class Command(BaseCommand):

    def handle(self, *args, **options):
        schedule = [
            # Проверка на др
            ScheduleItem("0 9 * * *", "check_birthday", "46"),
            # Автоостановка серверов по майну
            # ScheduleItem("*/30 * * * *", "auto_stop_servers"),
            # Проверка донатов
            ScheduleItem("*/30 * * * *", "check_donations", "46"),
            # Проверка оповещений
            ScheduleItem("*/1 * * * *", "check_notify"),
            # Проверка подписок
            ScheduleItem("*/10 * * * *", "check_subscribe"),
            # Получение гороскопа
            ScheduleItem("0 1 * * *", "get_horoscope"),
            # Сбор данных с яндекс такси
            ScheduleItem("* * * * *", "get_yandex_taxi_info"),
            # Отправка новостей Паше
            ScheduleItem("0 */6 * * *", "check_pasha_news", "130"),
        ]

        dt_now = localize_datetime(datetime.utcnow(), TIME_ZONE).replace(second=0, microsecond=0)

        for item in schedule:
            # Берём прошедшие события но в пределах 1 минуты
            if item.cron.previous(dt_now) != -60:
                continue
            args = [item.command]
            if item.args:
                args.append(item.args)
            threading.Thread(target=call_command, args=args).start()


class ScheduleItem:
    def __init__(self, cron: str, command: str, args: str = None, kwargs: dict = None):
        self.cron = CronTab(cron)
        self.command = command
        self.args = args
        self.kwargs = kwargs
