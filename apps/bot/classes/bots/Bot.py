import logging
import traceback
from threading import Thread

from apps.bot.classes.consts.Consts import Platform
from apps.bot.classes.consts.Exceptions import PWarning, PError, PSkip
from apps.bot.classes.messages.ResponseMessage import ResponseMessage, ResponseMessageItem
from apps.bot.models import Users, Chat, Bot as BotModel
from apps.bot.utils.utils import tanimoto
from apps.games.models import Gamer


class Bot(Thread):
    def __init__(self, platform):
        Thread.__init__(self)

        self.platform = platform
        self.mentions = []
        self.user_model = Users.objects.filter(platform=self.platform.name)
        self.chat_model = Chat.objects.filter(platform=self.platform.name)
        self.bot_model = BotModel.objects.filter(platform=self.platform.name)

        self.logger = logging.getLogger(platform.value)

    def run(self):
        """
        Thread запуск основного тела команды
        """
        self.listen()

    def listen(self):
        """
        Получение новых событий и их обработка
        """
        pass

    def handle_event(self, event, send=True):
        try:
            event.setup_event()
            if not event.need_a_response():
                return
            message = self.route(event)
            if message:
                self.parse_and_send_msgs(event.peer_id, message, send)
        except Exception as e:
            print(str(e))
            tb = traceback.format_exc()
            print(tb)

    def send_response_message(self, rm: ResponseMessage):
        for msg in rm.messages:
            response = self.send_message(msg)
            if response.status_code != 200:
                error_msg = "Непредвиденная ошибка. Сообщите разработчику. Команда /баг"
                error_rm = ResponseMessage(error_msg, msg.peer_id).messages[0]
                self.logger.error({'result': error_msg, 'error': response.json()['description']})
                self.send_message(error_rm)

    def parse_and_send_msgs(self, peer_id, msgs, send=True) -> ResponseMessage:
        """
        Отправка сообщения от команды. Принимает любой формат
        """
        rm = ResponseMessage(msgs, peer_id)
        if send:
            self.send_response_message(rm)
        return rm

    def parse_and_send_msgs_thread(self, peer_id, msgs):
        Thread(target=self.parse_and_send_msgs, args=(peer_id, msgs)).start()

    def route(self, event):
        """
        Выбор команды и отправка данных о сообщении ей
        """
        self.logger.debug(event.to_log())

        from apps.bot.initial import COMMANDS
        for command in COMMANDS:
            try:
                if command.accept(event):
                    result = command.__class__().check_and_start(self, event)
                    self.logger.debug({'result': result})
                    return result
            except (PWarning, PError) as e:
                msg = str(e)
                getattr(self.logger, e.level)({'result': msg})
                return msg
            # ToDo: check
            except PSkip:
                return
            except Exception as e:
                msg = "Непредвиденная ошибка. Сообщите разработчику. Команда /баг"
                log_exception = {
                    'exception': str(e),
                    'result': msg
                }
                self.logger.error(log_exception, exc_info=traceback.format_exc())
                return msg

        if event.chat and not event.chat.need_reaction:
            return

        similar_command = self.get_similar_command(event, COMMANDS)
        self.logger.debug({'result': similar_command})
        return similar_command

    @staticmethod
    def get_similar_command(event, commands):
        """
        Получение похожей команды по неправильно введённой
        """
        similar_command = None
        tanimoto_max = 0
        user_groups = event.sender.get_list_of_role_names()
        for command in commands:
            if not command.full_names:
                continue

            # Выдача пользователю только тех команд, которые ему доступны
            command_access = command.access
            if command_access.name not in user_groups:
                continue

            # Выдача только тех команд, у которых стоит флаг выдачи
            if not command.suggest_for_similar:
                continue

            for name in command.full_names:
                if name:
                    tanimoto_current = tanimoto(event.message.command, name)
                    if tanimoto_current > tanimoto_max:
                        tanimoto_max = tanimoto_current
                        similar_command = name

        msg = f"Я не понял команды \"{event.message.command}\"\n"
        if similar_command and tanimoto_max != 0:
            msg += f"Возможно вы имели в виду команду \"{similar_command}\""
        return msg

    def get_chat_by_id(self, chat_id) -> Chat:
        """
        Возвращает чат по его id
        """
        if chat_id > 0:
            chat_id *= -1
        tg_chat = self.chat_model.filter(chat_id=chat_id)
        if len(tg_chat) > 0:
            tg_chat = tg_chat.first()
        else:
            tg_chat = Chat(chat_id=chat_id, platform=self.platform.name)
            tg_chat.save()
        return tg_chat

    def send_message(self, rm: ResponseMessageItem):
        raise NotImplementedError

    @staticmethod
    def get_gamer_by_user(user) -> Gamer:
        """
        Получение игрока по модели пользователя
        """

        gamers = Gamer.objects.filter(user=user)
        if len(gamers) == 0:
            gamer = Gamer(user=user)
            gamer.save()
            return gamer
        elif len(gamers) > 1:
            raise PWarning("Два и более игрока подходит под поиск")
        else:
            return gamers.first()

    # ToDo: очень говнокод
    def get_user_by_name(self, args, filter_chat=None) -> Users:
        """
        Получение пользователя по имени/фамилии/имени и фамилии/никнейма/ид
        """
        if not args:
            raise PWarning("Отсутствуют аргументы")
        if isinstance(args, str):
            args = [args]
        users = self.user_model
        if filter_chat:
            users = users.filter(chats=filter_chat)
        if len(args) >= 2:
            user = users.filter(name=args[0].capitalize(), surname=args[1].capitalize())
        else:
            user = users.filter(nickname_real=args[0].capitalize())
            if len(user) == 0:
                user = users.filter(name=args[0].capitalize())
                if len(user) == 0:
                    user = users.filter(surname=args[0].capitalize())
                    if len(user) == 0:
                        user = users.filter(nickname=args[0])
                        if len(user) == 0:
                            user = users.filter(user_id=args[0])

        if len(user) > 1:
            raise PWarning("2 и более пользователей подходит под поиск")

        if len(user) == 0:
            raise PWarning("Пользователь не найден. Возможно опечатка или он мне ещё ни разу не писал")

        return user.first()

    @staticmethod
    def add_chat_to_user(user, chat):
        """
        Добавление чата пользователю
        """
        chats = user.chats
        if chat not in chats.all():
            chats.add(chat)

    @staticmethod
    def remove_chat_from_user(user, chat):
        """
        Удаление чата пользователю
        """
        chats = user.chats
        if chat in chats.all():
            chats.remove(chat)


def get_bot_by_platform(platform: Platform):
    """
    Получение бота по платформе
    """
    # from apps.bot.classes.bots.VkBot import VkBot
    from apps.bot.classes.bots.TgBot import TgBot
    # from apps.bot.classes.bots.YandexBot import YandexBot

    platforms = {
        # Platform.VK: VkBot,
        Platform.TG: TgBot,
        # Platform.YANDEX: YandexBot
    }
    return platforms[platform]


def get_moderator_bot_class():
    from apps.bot.classes.bots.TgBot import TgBot
    return TgBot()


def upload_image_to_vk_server(image):
    pass
    # ToDo
    # vk_bot = VkBot()
    # return vk_bot.upload_photo_and_get_absolute_url(image)
