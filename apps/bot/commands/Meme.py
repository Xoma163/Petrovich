import threading
from typing import List
from urllib.parse import urlparse, parse_qsl

import requests
from django.db.models import Q

from apps.bot.APIs.YoutubeVideoAPI import YoutubeVideoAPI
from apps.bot.classes.Command import Command
from apps.bot.classes.bots.Bot import send_message_to_moderator_chat
from apps.bot.classes.consts.Consts import Role, Platform, ATTACHMENT_TYPE_TRANSLATOR
from apps.bot.classes.consts.Exceptions import PWarning, PSkip
from apps.bot.classes.messages.attachments.GifAttachment import GifAttachment
from apps.bot.classes.messages.attachments.LinkAttachment import LinkAttachment
from apps.bot.classes.messages.attachments.PhotoAttachment import PhotoAttachment
from apps.bot.classes.messages.attachments.StickerAttachment import StickerAttachment
from apps.bot.classes.messages.attachments.VideoAttachment import VideoAttachment
from apps.bot.classes.messages.attachments.VideoNoteAttachment import VideoNoteAttachment
from apps.bot.classes.messages.attachments.VoiceAttachment import VoiceAttachment
from apps.bot.utils.utils import tanimoto, get_tg_formatted_text
from apps.service.models import Meme as MemeModel
from petrovich.settings import env


class Meme(Command):
    name = "мем"
    name_tg = "meme"

    help_text = "присылает мем"
    help_texts = [
        "- присылает рандомный мем",
        "(название/id) - присылает нужный мем. Можно использовать * вместо символов поиска. Например /мем ж*па",
        "добавить (название) (Вложение/Пересланное сообщение с вложением) - добавляет мем",
        "добавить (название) (ссылка на youtube/coub)  - добавляет мем с youtube/coub",
        "обновить (название/id) (Вложение/Пересланное сообщение с вложением) - обновляет созданный вами мем.",
        "обновить (название/id) (ссылка на youtube/coub) - обновляет созданный вами мем",
        "удалить (название/id) - удаляет созданный вами мем",
        "инфо (название/id) - присылает информацию по мему\n",

        "подтвердить - присылает мем на подтверждение (для модераторов)",
        "подтвердить (название/id) - подтверждает мем (для модераторов)",
        "отклонить (название/id) - отклоняет мем (для модераторов)",
        "переименовать (id) (новое название) - переименовывает мем (для модераторов)",
        "удалить (название/id) - удаляет мем (для модераторов)"
    ]

    priority = 70

    YOUTUBE_URLS = ['youtu.be', 'youtube.com']
    ALLOWED_URLS = YOUTUBE_URLS + ['coub.com']

    ALLOWED_ATTACHMENTS = [
        PhotoAttachment, VideoAttachment, StickerAttachment, GifAttachment, VoiceAttachment, VideoNoteAttachment
    ]

    def accept(self, event):
        if event.command:
            event.message.args = event.message.clear.split(' ')
            return True
        return super().accept(event)

    @staticmethod
    def accept_extra(event):
        if event.is_fwd:
            return False
        if event.message and not event.message.mentioned:
            if (event.is_from_chat and event.chat.need_meme and not event.message.mentioned) or event.is_from_user:
                message_is_exact_meme_name = MemeModel.objects.filter(name=event.message.clear, approved=True).exists()
                if message_is_exact_meme_name:
                    return True
        return False

    def start(self):
        if not self.event.message.args:
            return self.menu_random()

        arg0 = self.event.message.args[0]
        menu = [
            [['добавить'], self.menu_add],
            [['обновить'], self.menu_refresh],
            [['удалить'], self.menu_delete],
            [['подтвердить', 'принять', '+'], self.menu_approve],
            [['отклонить', 'отменить', '-'], self.menu_reject],
            [['переименовать', 'правка'], self.menu_rename],
            [['инфо'], self.menu_info],
            [['default'], self.menu_default]
        ]
        method = self.handle_menu(menu, arg0)
        return method()

    # MENU #

    def menu_add(self):
        self.check_args(2)
        attachments = self.event.get_all_attachments(self.ALLOWED_ATTACHMENTS)
        if len(attachments) == 0:
            url = self.event.message.args_case[-1]
            self._check_allowed_url(url)

            attachment = LinkAttachment()
            attachment.url = url
            meme_name_list = self.event.message.args[1:-1]
        else:
            meme_name_list = self.event.message.args[1:]
            attachment = attachments[0]

        self.check_meme_name_is_no_digits(meme_name_list)
        meme_name = " ".join(meme_name_list)

        new_meme = {
            'name': meme_name,
            'type': attachment.type,
            'author': self.event.sender,
            'approved': self.event.sender.check_role(Role.MODERATOR) or self.event.sender.check_role(Role.TRUSTED)
        }

        ban_list = ['добавить', 'обновить', 'удалить', 'конфа', 'рандом', 'р', 'подтвердить', 'принять', '+',
                    'отклонить', 'отменить', '-', 'переименовать', 'правка', 'инфо']
        if new_meme['name'] in ban_list:
            raise PWarning("Мем с таким названием нельзя создать")

        try:
            MemeModel.objects.get(name=new_meme['name'])
            raise PWarning("Мем с таким названием уже есть в базе")
        except MemeModel.DoesNotExist:
            pass

        if isinstance(attachment, LinkAttachment):
            new_meme['link'] = attachment.url
        else:
            new_meme['tg_file_id'] = attachment.file_id
        new_meme_obj = MemeModel.objects.create(**new_meme)

        # Кэш
        if isinstance(attachment, LinkAttachment) and self._is_youtube_url(attachment.url):
            self.set_youtube_file_id(new_meme_obj)
        if new_meme['approved']:
            return "Добавил"

        meme_to_send = self.prepare_meme_to_send(new_meme_obj)
        meme_to_send['text'] = "Запрос на подтверждение мема:\n" \
                               f"{new_meme_obj.author}\n" \
                               f"{new_meme_obj.name} ({new_meme_obj.id})"

        button_approve = self.bot.get_button("Подтвердить", self.name, args=["подтвердить", new_meme_obj.pk])
        button_decline = self.bot.get_button("Отклонить", self.name, args=["отклонить", new_meme_obj.pk])
        meme_to_send['keyboard'] = self.bot.get_inline_keyboard([button_approve, button_decline])

        # Отправка сообщения в модераторную
        send_message_to_moderator_chat(meme_to_send)
        return "Добавил. Воспользоваться мемом можно после проверки модераторами."

    def menu_refresh(self):
        self.check_args(2)
        try:
            url = self.event.message.args_case[-1]
            self._check_allowed_url(url)
            attachment = LinkAttachment()
            attachment.url = url
            attachments = [attachment]
            id_name = self.get_id_or_meme_name(self.event.message.args[1:-1])
        except PWarning:
            attachments = self.event.get_all_attachments(self.ALLOWED_ATTACHMENTS)
            id_name = self.get_id_or_meme_name(self.event.message.args[1:])

        meme_filter = {}
        if isinstance(id_name, int):
            meme_filter['_id'] = id_name
        else:
            meme_filter['filter_list'] = id_name.split(' ')
        if not (self.event.sender.check_role(Role.MODERATOR) or self.event.sender.check_role(Role.TRUSTED)):
            meme_filter['filter_user'] = self.event.sender

        meme = self.get_meme(**meme_filter)

        if len(attachments) == 0:
            raise PWarning("Не нашёл вложений в сообщении или пересланном сообщении\n"
                           "Не нашёл ссылки на youtube/coub")

        attachment = attachments[0]
        fields = {'type': attachment.type}
        if isinstance(attachment, LinkAttachment):
            fields['link'] = attachment.url
        else:
            fields['tg_file_id'] = attachment.file_id

        for attr, value in fields.items():
            setattr(meme, attr, value)
        meme.save()
        # Кэш
        if isinstance(attachment, LinkAttachment) and self._is_youtube_url(attachment.url):
            self.set_youtube_file_id(meme)

        if self.event.sender.check_role(Role.MODERATOR) or self.event.sender.check_role(Role.TRUSTED):
            return f'Обновил мем "{meme.name}"'

        meme_to_send = self.prepare_meme_to_send(meme)
        meme_to_send['text'] = "Запрос на обновление мема:\n" \
                               f"{meme.author}\n" \
                               f"{meme.name} ({meme.id})"

        send_message_to_moderator_chat(meme_to_send)

        return "Обновил. Воспользоваться мемом можно после проверки модераторами."

    def menu_delete(self):
        self.check_args(2)
        meme_filter = self.get_default_meme_filter_by_args(self.event.message.args[1:])
        if not self.event.sender.check_role(Role.MODERATOR):
            meme_filter['filter_user'] = self.event.sender
        meme = self.get_meme(**meme_filter)

        # Если удаляем мем другого человека, шлём ему сообщением
        if self.event.sender.check_role(Role.MODERATOR) and meme.author != self.event.sender:
            user_msg = f'Мем с названием "{meme.name}" удалён поскольку он не ' \
                       f'соответствует правилам или был удалён автором.'
            if meme.author:
                user = meme.author.get_tg_user()
                self.bot.parse_and_send_msgs(user_msg, user.user_id, self.event.message_thread_id)

        meme_name = meme.name
        meme.delete()
        return f'Удалил мем "{meme_name}"'

    def menu_random(self):
        meme = MemeModel.objects.filter(approved=True).order_by('?').first()
        return self.prepare_meme_to_send(meme, print_name=True, send_keyboard=True)

    def menu_approve(self):
        self.check_sender(Role.MODERATOR)

        if len(self.event.message.args) == 1:
            meme = self.get_meme(approved=False)
            meme_to_send = self.prepare_meme_to_send(meme)
            meme_to_send['text'] = f"{meme.author}\n" \
                                   f"{meme.name} ({meme.id})"
            return meme_to_send

        self.check_args(2)

        meme_filter = self.get_default_meme_filter_by_args(self.event.message.args[1:])
        meme = self.get_meme(**meme_filter)

        if meme.approved:
            raise PWarning("Мем уже подтверждён")

        user_msg = f'Мем с названием "{meme.name}" подтверждён.'
        user = meme.author.get_tg_user()
        self.bot.parse_and_send_msgs(user_msg, user.user_id, self.event.message_thread_id)

        msg = f'Мем "{meme.name}" ({meme.id}) подтверждён'
        meme.approved = True
        meme.save()
        return msg

    def menu_reject(self):
        self.check_sender(Role.MODERATOR)
        self.check_args(2)

        meme_filter = self.get_default_meme_filter_by_args(self.event.message.args[1:])
        meme = self.get_meme(**meme_filter)
        if meme.approved:
            raise PWarning("Нельзя отклонить уже подтверждённый мем")

        msg = f'Мем "{meme.name}" ({meme.id}) отклонён'
        user = meme.author.get_tg_user()
        self.bot.parse_and_send_msgs(msg, user.user_id, self.event.message_thread_id)

        meme.delete()
        return msg

    def menu_rename(self):
        self.check_sender(Role.MODERATOR)
        self.check_args(3)
        self.int_args = [1]
        self.parse_int()
        meme = self.get_meme(_id=self.event.message.args[1])

        new_name_list = self.event.message.args[2:]
        self.check_meme_name_is_no_digits(new_name_list)
        new_name = " ".join(new_name_list)

        try:
            MemeModel.objects.get(name=new_name)
            raise PWarning("Мем с таким названием уже есть")
        except MemeModel.DoesNotExist:
            pass

        user_msg = f'Мем с названием "{meme.name}" переименован.\n' \
                   f'Новое название - "{new_name}"'

        meme.name = new_name
        meme.save()

        if meme.author != self.event.sender:
            user = meme.author.get_tg_user()
            self.bot.parse_and_send_msgs(user_msg, user.user_id, self.event.message_thread_id)
        return user_msg

    def menu_info(self):
        self.check_args(2)
        meme_filter = self.get_default_meme_filter_by_args(self.event.message.args[1:])
        meme = self.get_meme(**meme_filter)
        return meme.get_info()

    def menu_default(self):
        warning_message = None

        id_name = self.get_id_or_meme_name(self.event.message.args)
        if isinstance(id_name, int):
            meme = self.get_meme(_id=id_name)
        else:
            memes = self.get_filtered_memes(self.event.message.args)
            try:
                meme = self.get_one_meme(memes, self.event.message.args)
            except PWarning:
                tanimoto_memes = self.get_tanimoto_memes(memes, " ".join(self.event.message.args))
                if len(tanimoto_memes) == 0:
                    raise PWarning("Не нашёл :(")
                meme = tanimoto_memes[0]
                warning_message = self.get_similar_memes_names(tanimoto_memes)

        meme.uses += 1
        meme.save()
        prepared_meme = self.prepare_meme_to_send(meme)
        if warning_message:
            if self.event.platform == Platform.TG:
                return [prepared_meme, get_tg_formatted_text(warning_message)]
            return [prepared_meme, warning_message]
        return prepared_meme

    def get_filtered_memes(self, filter_list=None, filter_user=None, approved=True, _id=None):
        memes = MemeModel.objects
        if _id:
            memes = memes.filter(id=_id)
        else:
            if filter_list is None:
                filter_list = []
            memes = memes.filter(approved=approved)
            if self.event.platform == Platform.TG:
                memes = memes.exclude(type='audio')
            if filter_list:
                filter_list = list(map(lambda x: x.lower(), filter_list))
                for _filter in filter_list:
                    if '*' in _filter:
                        _filter = _filter.replace('*', '.')
                        regex_filter = fr'.*{_filter}.*'
                        memes = memes.filter(name__iregex=regex_filter)
                    else:
                        memes = memes.filter(name__contains=_filter)

        if filter_user:
            memes = memes.filter(author=filter_user)
        return memes

    @staticmethod
    def get_one_meme(memes, filter_list, approved=True) -> MemeModel:
        if len(memes) == 0:
            raise PWarning("Не нашёл :(")
        elif len(memes) == 1:
            return memes.first()
        elif not approved:
            return memes.first()
        else:
            filters_str = " ".join(filter_list)
            for meme in memes:
                if meme.name == filters_str:
                    return meme
            raise PWarning("Под запрос подходит 2 и более мема")

    def get_meme(self, filter_list=None, filter_user=None, approved=True, _id=None) -> MemeModel:
        """
        :return: 1 мем. Если передан параметр use_tanimoto, то список мемов отсортированных по коэфф. Танимото
        """
        memes = self.get_filtered_memes(filter_list, filter_user, approved, _id)
        meme = self.get_one_meme(memes, filter_list, approved)
        return meme

    def prepare_meme_to_send(self, meme, print_name=False, send_keyboard=False):
        msg = {}

        if self.event.platform == Platform.TG:

            if meme.tg_file_id:
                att = ATTACHMENT_TYPE_TRANSLATOR[meme.type]()
                att.file_id = meme.tg_file_id
                msg['attachments'] = att
            elif meme.type == LinkAttachment.TYPE:
                y_api = YoutubeVideoAPI()
                try:
                    content_url = y_api.get_video_download_url(meme.link, self.event.platform)
                    video_content = requests.get(content_url).content
                    msg['attachments'] = self.bot.get_video_attachment(video_content, peer_id=self.event.peer_id)
                    msg['text'] = y_api.get_timecode_str(meme.link)
                    self.set_youtube_file_id(meme)
                    # return
                except PSkip:
                    msg['text'] = meme.link
                except Exception as e:
                    raise e
            else:
                msg['text'] = meme.link

        if print_name:
            if msg.get('text', None):
                msg['text'] += f"\n{meme.name}"

        if send_keyboard:
            button = self.bot.get_button("Ещё", self.name)
            msg['keyboard'] = self.bot.get_inline_keyboard([button])
        return msg

    def _check_allowed_url(self, url):
        parsed_url = urlparse(url)
        if not parsed_url.hostname:
            raise PWarning("Не нашёл ссылку на youtube видео")

        if parsed_url.hostname.replace('www.', '').lower() not in self.ALLOWED_URLS:
            raise PWarning("Это ссылка не на youtube/coub видео")

    def _is_youtube_url(self, url):
        parsed_url = urlparse(url)
        return parsed_url.hostname.replace('www.', '').lower() in self.YOUTUBE_URLS

    def set_youtube_file_id(self, meme):
        thread = threading.Thread(target=self._set_youtube_file_id, args=(meme,))
        thread.start()

    def _set_youtube_file_id(self, meme):
        from apps.bot.models import Chat

        y_api = YoutubeVideoAPI()
        msg = {}
        try:
            content_url = y_api.get_video_download_url(meme.link, self.event.platform)
            video_content = requests.get(content_url).content

            video_uploading_chat = Chat.objects.get(pk=env.str("TG_PHOTO_UPLOADING_CHAT_PK"))
            video = self.bot.get_video_attachment(video_content, peer_id=video_uploading_chat.chat_id)
            parsed_url = urlparse(meme.link)
            video_id = parsed_url.path.strip('/')
            video.thumb = f"https://img.youtube.com/vi/{video_id}/default.jpg"
            msg['attachments'] = [video]
            r = self.bot.parse_and_send_msgs(msg, video_uploading_chat.chat_id, self.event.message_thread_id)
            r_json = r[0]['response'].json()
            self.bot.delete_message(video_uploading_chat.chat_id, r_json['result']['message_id'])
            file_id = r_json['result']['video']['file_id']
            meme.tg_file_id = file_id
            meme.save()
            return
        except Exception:
            return

    @staticmethod
    def get_tanimoto_memes(memes, filter_list) -> List[MemeModel]:
        query = " ".join(filter_list)
        memes_list = []
        for meme in memes:
            tanimoto_coefficient = tanimoto(meme.name, query)
            memes_list.append({'meme': meme, 'tanimoto': tanimoto_coefficient, 'contains_query': query in meme.name})
        memes_list.sort(key=lambda x: (x['contains_query'], x['tanimoto']), reverse=True)
        memes_list = [meme['meme'] for meme in memes_list]
        return memes_list

    def get_similar_memes_names(self, memes):
        meme_name_limit = 50
        meme_count_limit = 10
        if self.event.platform == Platform.TG:
            meme_name_limit = 120
            meme_count_limit = 20
        total_memes_count = len(memes)
        memes = memes[:meme_count_limit]
        meme_names = []
        for meme in memes:
            if len(meme.name) < meme_name_limit:
                meme_names.append(meme.name)
            else:
                meme_names.append(meme.name[:meme_name_limit] + "...")
        meme_names_str = ";\n".join(meme_names)

        msg = f"Нашёл сразу {total_memes_count}, уточните:\n\n" \
              f"{meme_names_str}" + '.'
        if total_memes_count > meme_count_limit:
            msg += "\n..."
        return msg

    @staticmethod
    def get_id_or_meme_name(args):
        """
        Возвращает int если это id и передан только один аргумент.
        Возвращает str если это name
        """
        if isinstance(args, str):
            args = [args]
        if len(args) == 1:
            try:
                _id = int(args[0])
                return _id
            except ValueError:
                pass
        return " ".join(args)

    def get_default_meme_filter_by_args(self, args):
        id_name = self.get_id_or_meme_name(args)

        meme_filter = {}
        if isinstance(id_name, int):
            meme_filter['_id'] = id_name
        else:
            meme_filter['filter_list'] = id_name.split(' ')
        return meme_filter

    @staticmethod
    def check_meme_name_is_no_digits(meme_name_list):
        try:
            _ = [int(x) for x in meme_name_list]
            raise PWarning("Название мема не может состоять только из цифр")
        except ValueError:
            pass

    @staticmethod
    def _get_inline_qrs(memes):
        _inline_qr = []
        for meme in memes:
            # Todo: send sticker as sticker
            qr = {
                'id': meme.pk,
                'type': meme.type
            }
            if meme.type in [PhotoAttachment.TYPE]:
                qr.update({
                    'photo_file_id': meme.tg_file_id,
                })
            elif meme.type in [StickerAttachment.TYPE]:
                qr.update({
                    'sticker_file_id': meme.tg_file_id,
                })
            elif meme.type in [VideoAttachment.TYPE]:
                if meme.tg_file_id:
                    qr.update({
                        'video_file_id': meme.tg_file_id,
                        'title': meme.name,
                    })
                else:
                    continue

            elif meme.type in [GifAttachment.TYPE]:
                qr.update({
                    'gif_file_id': meme.tg_file_id,
                    'title': meme.name,
                })
            elif meme.type in [VoiceAttachment.TYPE]:
                qr.update({
                    'voice_file_id': meme.tg_file_id,
                    'title': meme.name,
                })
            elif meme.type == LinkAttachment.TYPE:
                parsed_url = urlparse(meme.link)
                video_id = parsed_url.path.strip('/')
                if parsed_url.query:
                    # dict cast
                    query_dict = {x[0]: x[1] for x in parse_qsl(parsed_url.query)}
                    v = query_dict.get('v', None)
                    if v:
                        video_id = v

                y_api = YoutubeVideoAPI()
                ts = y_api.get_timecode_str(meme.link)

                if meme.tg_file_id:
                    qr.update({
                        'id': meme.pk,
                        'type': 'video',
                        'video_file_id': meme.tg_file_id,
                        'title': meme.name,
                    })
                else:
                    qr = {
                        'id': meme.pk,
                        'type': "video",
                        'video_url': meme.link,
                        'mime_type': "text/html",
                        'title': meme.name,
                        'thumb_url': f"https://img.youtube.com/vi/{video_id}/default.jpg",
                        'input_message_content': {
                            'message_text': meme.link
                        }
                    }
                if ts:
                    qr['caption'] = ts
            else:
                raise RuntimeError()
            _inline_qr.append(qr)

        return _inline_qr

    def get_tg_inline_memes(self, filter_list, max_count=10):
        if filter_list:
            filtered_memes = self.get_filtered_memes(filter_list)
        else:
            filtered_memes = MemeModel.objects.all().order_by('-uses')

        q = Q(approved=True) & (
                Q(type='link', link__icontains="youtu") |
                Q(type__in=['photo', 'sticker', 'video', 'voice', 'gif']))
        memes = filtered_memes.filter(q)

        all_memes_qr = []
        try:
            this_meme = self.get_one_meme(memes, filter_list)
            this_meme_qr = self._get_inline_qrs([this_meme])
            all_memes_qr += this_meme_qr
            memes = memes.exclude(pk=this_meme.pk)
        except PWarning:
            pass

        memes = memes[:max_count]
        memes = self.get_tanimoto_memes(memes, filter_list)
        # ToDo: wtf?
        att_types = [
            VoiceAttachment.TYPE,
            LinkAttachment.TYPE,
            VideoAttachment.TYPE,
            GifAttachment.TYPE,
            StickerAttachment.TYPE,
            PhotoAttachment.TYPE
        ]
        for att_type in att_types:
            all_memes_qr += self._get_inline_qrs(list(filter(lambda x: x.type == att_type, memes)))
        return all_memes_qr
