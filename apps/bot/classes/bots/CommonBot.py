import threading
import traceback

from apps.bot.classes.Consts import Role
from apps.bot.classes.common.CommonMethods import tanimoto, check_user_group, get_user_groups
from apps.bot.classes.events.Event import Event
from apps.service.views import append_command_to_statistics


class CommonBot():
    def __init__(self):
        self.mentions = []
        self.BOT_CAN_WORK = True
        self.DEBUG = False
        self.DEVELOP_DEBUG = False

        self.user_model = None
        self.chat_model = None
        self.bot_model = None

        self.logger = None

    def run(self):
        self.listen()

    def listen(self):
        pass

    def menu(self, event, send=True):

        # Проверяем не остановлен ли бот, если так, то проверяем вводимая команда = старт?
        if not self.can_bot_working():
            if not check_user_group(event.sender, Role.ADMIN):
                return

            if event.command in ['старт']:
                self.BOT_CAN_WORK = True
                # cameraHandler.resume()
                msg = "Стартуем!"
                self.send_message(event.peer_id, msg)
                log_result = {'result': msg}
                self.logger.debug(log_result)
                return msg
            return

        group = event.sender.groups.filter(name=Role.BANNED.name)
        if len(group) > 0:
            return

        if self.DEBUG and send:
            if hasattr(event, 'payload') and event.payload:
                debug_message = \
                    f"msg = {event.msg}\n" \
                    f"command = {event.command}\n" \
                    f"args = {event.args}\n" \
                    f"payload = {event.payload}\n"
            else:
                debug_message = \
                    f"msg = {event.msg}\n" \
                    f"command = {event.command}\n" \
                    f"args = {event.args}\n" \
                    f"original_args = {event.original_args}\n"
            self.send_message(event.peer_id, debug_message)

        log_event = event
        self.logger.debug(log_event)

        from apps.bot.initial import get_commands
        commands = get_commands()
        for command in commands:
            try:
                if command.accept(event):
                    result = command.__class__().check_and_start(self, event)
                    if send:
                        self.parse_and_send_msgs(event.peer_id, result)
                    append_command_to_statistics(event.command)
                    log_result = {'result': result}
                    self.logger.debug(log_result)
                    return result
            except RuntimeWarning as e:
                msg = str(e)
                log_runtime_warning = {'result': msg}
                self.logger.warning(log_runtime_warning)

                if send:
                    self.parse_and_send_msgs(event.peer_id, msg)
                return msg
            except RuntimeError as e:
                exception = str(e)
                log_runtime_error = {'exception': exception, 'result': exception}
                self.logger.error(log_runtime_error)
                if send:
                    self.parse_and_send_msgs(event.peer_id, exception)
                return exception
            except Exception as e:
                msg = "Непредвиденная ошибка. Сообщите разработчику в группе или команда /баг"
                tb = traceback.format_exc()
                log_exception = {
                    'exception': str(e),
                    'result': msg
                }
                self.logger.error(log_exception, exc_info=tb)
                if send:
                    self.parse_and_send_msgs(event.peer_id, msg)
                return msg

        if event.chat and not event.chat.need_reaction:
            return None
        similar_command = commands[0].names[0]
        tanimoto_max = 0
        user_groups = get_user_groups(event.sender)
        for command in commands:
            # Выдача пользователю только тех команд, которые ему доступны
            command_access = command.access
            if isinstance(command_access, str):
                command_access = [command_access]
            if command_access.name not in user_groups:
                continue

            for name in command.names:
                if name:
                    tanimoto_current = tanimoto(event.command, name)
                    if tanimoto_current > tanimoto_max:
                        tanimoto_max = tanimoto_current
                        similar_command = name

        msg = f"Я не понял команды \"{event.command}\"\n"
        if tanimoto_max != 0:
            msg += f"Возможно вы имели в виду команду \"{similar_command}\""
        self.logger_result = {'result': msg}
        self.logger.debug(self.logger_result)
        if send:
            self.send_message(event.peer_id, msg)
        return msg

    def send_message(self, peer_id, msg="ᅠ", attachments=None, keyboard=None, dont_parse_links=False, **kwargs):
        pass

    def parse_and_send_msgs(self, peer_id, result):
        if isinstance(result, str) or isinstance(result, int) or isinstance(result, float):
            result = {'msg': result}
        if isinstance(result, dict):
            result = [result]
        if isinstance(result, list):
            for msg in result:
                if isinstance(msg, str):
                    msg = {'msg': msg}
                if isinstance(msg, dict):
                    self.send_message(peer_id, **msg)

    # Отправляет сообщения юзерам в разных потоках
    def parse_and_send_msgs_thread(self, chat_ids, message):
        if not isinstance(chat_ids, list):
            chat_ids = [chat_ids]
        for chat_id in chat_ids:
            thread = threading.Thread(target=self.parse_and_send_msgs, args=(chat_id, message,))
            thread.start()

    def need_a_response(self, event):
        message = event['message']['text']
        from_user = event['from_user']
        have_audio_message = self.have_audio_message(event)
        if have_audio_message:
            return True
        have_action = event['message']['action'] is not None
        if have_action:
            return True
        if len(message) == 0:
            return False
        if from_user:
            return True
        if message[0] == '/':
            return True
        for mention in self.mentions:
            if message.find(mention) != -1:
                return True
        return False

    # def get_user_by_id(self, user_id):
    #     pass
    #
    # @staticmethod
    # def get_chat_by_id(chat_id):
    #     pass

    @staticmethod
    def have_audio_message(event):
        if isinstance(event, Event):
            all_attachments = event.attachments or []
            if event.fwd:
                all_attachments += event.fwd[0]['attachments']
            if all_attachments:
                for attachment in all_attachments:
                    if attachment['type'] == 'audio_message':
                        return True
        else:
            all_attachments = event['message']['attachments'].copy()
            if event['fwd']:
                all_attachments += event['fwd'][0]['attachments']
            if all_attachments:
                for attachment in all_attachments:
                    if attachment['type'] == 'audio_message':
                        # Костыль, чтобы при пересланном сообщении он не выполнял никакие другие команды
                        # event['message']['text'] = ''
                        return True
        return False

    @staticmethod
    def parse_date(date):
        date_arr = date.split('.')
        if len(date_arr) == 2:
            return f"1970-{date_arr[1]}-{date_arr[0]}"
        else:
            return f"{date_arr[2]}-{date_arr[1]}-{date_arr[0]}"

    @staticmethod
    def add_group_to_user(user, chat):
        chats = user.chats
        if chat not in chats.all():
            chats.add(chat)

    @staticmethod
    def remove_group_from_user(user, chat):
        chats = user.chats
        if chat in chats.all():
            chats.remove(chat)

    def can_bot_working(self):
        return self.BOT_CAN_WORK
