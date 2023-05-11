import re
from urllib.parse import urlparse

import requests
import youtube_dl
from urllib3.exceptions import MaxRetryError

from apps.bot.APIs.InstagramAPI import InstagramAPI
from apps.bot.APIs.PikabuAPI import PikabuAPI
from apps.bot.APIs.PinterestAPI import PinterestAPI
from apps.bot.APIs.RedditSaver import RedditSaver
from apps.bot.APIs.TheHoleAPI import TheHoleAPI
from apps.bot.APIs.TikTokDownloaderAPI import TikTokDownloaderAPI
from apps.bot.APIs.WASDAPI import WASDAPI
from apps.bot.APIs.YandexMusicAPI import YandexMusicAPI
from apps.bot.APIs.YoutubeMusicAPI import YoutubeMusicAPI
from apps.bot.APIs.YoutubeVideoAPI import YoutubeVideoAPI
from apps.bot.classes.Command import Command
from apps.bot.classes.bots.tg.TgBot import TgBot
from apps.bot.classes.consts.Consts import Platform
from apps.bot.classes.consts.Exceptions import PWarning, PSkip
from apps.bot.models import Chat
from apps.bot.utils.NothingLogger import NothingLogger
from apps.bot.utils.utils import get_urls_from_text
from petrovich.settings import env

YOUTUBE_URLS = ('www.youtube.com', 'youtube.com', "www.youtu.be", "youtu.be")
YOUTUBE_MUSIC_URLS = ("music.youtube.com",)
REDDIT_URLS = ("www.reddit.com",)
TIKTOK_URLS = ("www.tiktok.com", 'vm.tiktok.com', 'm.tiktok.com', 'vt.tiktok.com')
INSTAGRAM_URLS = ('www.instagram.com', 'instagram.com')
TWITTER_URLS = ('www.twitter.com', 'twitter.com')
PIKABU_URLS = ('www.pikabu.ru', 'pikabu.ru')
THE_HOLE_URLS = ('www.the-hole.tv', 'the-hole.tv')
WASD_URLS = ('www.wasd.tv', 'wasd.tv')
YANDEX_MUSIC_URLS = ('music.yandex.ru',)
PINTEREST_URLS = ('pinterest.com', 'ru.pinterest.com', 'www.pinterest.com', 'pin.it')

MEDIA_URLS = tuple(
    list(YOUTUBE_URLS) +
    list(YOUTUBE_MUSIC_URLS) +
    list(REDDIT_URLS) +
    list(TIKTOK_URLS) +
    list(INSTAGRAM_URLS) +
    list(TWITTER_URLS) +
    list(PIKABU_URLS) +
    list(THE_HOLE_URLS) +
    list(WASD_URLS) +
    list(YANDEX_MUSIC_URLS) +
    list(PINTEREST_URLS)
)


class Media(Command):
    name = "медиа"
    help_text = "скачивает видео из соцсетей и присылает его"
    help_texts = ["(ссылка на видео) - скачивает видео из соцсетей и присылает его"]
    help_texts_extra = "Поддерживаемые соцсети: Reddit/TikTok/YouTube/Instagram/Twitter/Pikabu/TheHole/Yandex Music/Pinterest\n\n" \
                       "Ключ --nomedia позволяет не запускать команду\n" \
                       "Ключ --audio позволяет скачивать аудиодорожку для видео с ютуба"
    platforms = [Platform.TG]

    bot: TgBot

    @staticmethod
    def accept_extra(event):
        if event.message and not event.message.mentioned:
            if "nomedia" in event.message.keys:
                return False
            all_urls = get_urls_from_text(event.message.clear_case)
            has_fwd_with_message = event.fwd and event.fwd[0].message and event.fwd[0].message.clear_case
            if event.is_from_pm and has_fwd_with_message:
                all_urls += get_urls_from_text(event.fwd[0].message.clear_case)
            for url in all_urls:
                message_is_media_link = urlparse(url).hostname in MEDIA_URLS
                if message_is_media_link:
                    return True
        return False

    def start(self):
        if self.event.message.command in self.full_names:
            if self.event.message.args:
                source = self.event.message.args_case[0]
            elif self.event.fwd:
                source = self.event.fwd[0].message.raw
            else:
                raise PWarning("Для работы команды требуются аргументы или пересылаемые сообщения")
            has_command_name = True
        else:
            source = self.event.message.raw
            has_command_name = False

        method, chosen_url = self.get_method_and_chosen_url(source)

        try:
            attachments, title = method(chosen_url)
        except PWarning as e:
            # Если была вызвана команда или отправлено сообщение в лс
            if has_command_name or self.event.is_from_pm:
                raise e
            else:
                raise PSkip()

        chosen_url_pos = source.find(chosen_url)

        text = ""
        if title:
            text = f"{title}\n"
        if self.event.is_from_chat:
            text += f"\nОт {self.event.sender}"

        source_hostname = str(urlparse(chosen_url).hostname).lstrip('www.')
        text += f'\nИсточник: {self.bot.get_formatted_url(source_hostname, chosen_url)}'

        # Костыль, чтобы видосы которые шарятся с мобилы с реддита не дублировали title

        extra_text = source[:chosen_url_pos].strip() + "\n" + source[chosen_url_pos + len(chosen_url):].strip()
        for key in self.event.message.keys:
            extra_text = extra_text.replace(self.event.message.KEYS_STR + key, "")
            extra_text = extra_text.replace(self.event.message.KEYS_SYMBOL + key, "")
        extra_text = extra_text.strip()
        if extra_text and extra_text != title:
            text += f"\n\n{extra_text}"

        reply_to = None
        if self.event.fwd:
            reply_to = self.event.fwd[0].message.id

        res = self.bot.parse_and_send_msgs({'text': text, 'attachments': attachments, 'reply_to': reply_to},
                                           self.event.peer_id, self.event.message_thread_id)
        if res[0]['success']:
            self.bot.delete_message(self.event.peer_id, self.event.message.id)

    def get_method_and_chosen_url(self, source):
        MEDIA_TRANSLATOR = {
            YOUTUBE_URLS: self.get_youtube_video,
            YOUTUBE_MUSIC_URLS: self.get_youtube_audio,
            TIKTOK_URLS: self.get_tiktok_video,
            REDDIT_URLS: self.get_reddit_attachment,
            INSTAGRAM_URLS: self.get_instagram_attachment,
            TWITTER_URLS: self.get_twitter_video,
            PIKABU_URLS: self.get_pikabu_video,
            THE_HOLE_URLS: self.get_the_hole_video,
            WASD_URLS: self.get_wasd_video,
            YANDEX_MUSIC_URLS: self.get_yandex_music,
            PINTEREST_URLS: self.get_pinterest_attachment,
        }

        urls = get_urls_from_text(source)
        for url in urls:
            hostname = urlparse(url).hostname
            if not hostname:
                raise PWarning("Не нашёл ссылки")
            for k in MEDIA_TRANSLATOR:
                if hostname in k:
                    return MEDIA_TRANSLATOR[k], url

        raise PWarning("Не youtube/tiktok/reddit/instagram ссылка")

    def get_youtube_video(self, url):
        y_api = YoutubeVideoAPI()
        if 'audio' in self.event.message.keys:
            return self.get_youtube_audio(url)
        else:
            content_url = y_api.get_video_download_url(url, self.event.platform)
            video_content = requests.get(content_url).content
            attachments = [
                self.bot.get_video_attachment(video_content, peer_id=self.event.peer_id, filename=y_api.filename)]

        text = y_api.title
        timecode = y_api.get_timecode_str(url)
        if timecode:
            text = f"{text}\n\n{timecode}"
        return attachments, text

    def get_youtube_audio(self, url):
        track = YoutubeMusicAPI(url)
        track.get_info()
        title = f"{track.artists} - {track.title}"
        audio_att = self.bot.get_audio_attachment(track.content, peer_id=self.event.peer_id,
                                                  filename=f"{title}.{track.format}",
                                                  thumb=track.cover_url, artist=track.artists, title=track.title)
        # audio_att.download_content()
        return [audio_att], ""

    def get_tiktok_video(self, url):
        ttd_api = TikTokDownloaderAPI()
        video_url = ttd_api.get_video_url(url)
        video = requests.get(video_url).content

        attachments = [self.bot.get_video_attachment(video, peer_id=self.event.peer_id, filename="tiktok.mp4")]
        return attachments, None

    def get_reddit_attachment(self, url):
        rs = RedditSaver()
        attachment = rs.get_from_reddit(url)
        if rs.is_gif:
            attachments = self.bot.get_gif_attachment(attachment, filename=rs.filename)
        elif rs.is_image or rs.is_images or rs.is_gallery:
            attachments = self.bot.get_photo_attachment(attachment, peer_id=self.event.peer_id, filename=rs.filename)
        elif rs.is_video:
            attachments = self.bot.get_video_attachment(attachment, peer_id=self.event.peer_id, filename=rs.filename)

        elif rs.is_text or rs.is_link:
            text = attachment
            all_photos = []
            text = text.replace("&#x200B;", "").replace("&amp;#x200B;", "").replace("&amp;", "&").replace(" ",
                                                                                                          " ").strip()
            p = re.compile(r"\[(.*)\]\(([^\)]*)\)")  # markdown links
            for item in reversed(list(p.finditer(text))):
                start_pos = item.start()
                end_pos = item.end()
                link_text = text[item.regs[1][0]:item.regs[1][1]]
                link = text[item.regs[2][0]:item.regs[2][1]]
                tg_url = self.bot.get_formatted_url(link_text, link)
                text = text[:start_pos] + tg_url + text[end_pos:]

            regexps_with_static = ((r"https.*player", "Видео"), (r"https://preview\.redd\.it/.*", "Фото"))
            for regexp, _text in regexps_with_static:
                p = re.compile(regexp)
                for item in reversed(list(p.finditer(text))):
                    start_pos = item.start()
                    end_pos = item.end()
                    if text[start_pos - 9:start_pos] == "<a href=\"":
                        continue
                    link = text[start_pos:end_pos]
                    tg_url = self.bot.get_formatted_url(_text, link)
                    text = text[:start_pos] + tg_url + text[end_pos:]
                    if _text == "Фото":
                        all_photos.append(link)
            p = re.compile(r'\*\*(.*)\*\*')  # markdown bold
            for item in reversed(list(p.finditer(text))):
                start_pos = item.start()
                end_pos = item.end()
                bold_text = text[item.regs[1][0]:item.regs[1][1]]
                tg_bold_text = self.bot.get_bold_text(bold_text).replace("**", '')
                text = text[:start_pos] + tg_bold_text + text[end_pos:]

            p = re.compile(r'&gt;(.*)\n')  # markdown quote
            for item in reversed(list(p.finditer(text))):
                start_pos = item.start()
                end_pos = item.end()
                quote_text = text[item.regs[1][0]:item.regs[1][1]]
                tg_quote_text = self.bot.get_formatted_text_line(quote_text)
                text = text[:start_pos] + tg_quote_text + text[end_pos:]
            if all_photos:
                msg = {'attachments': [self.bot.get_photo_attachment(x, filename=rs.filename) for x in all_photos]}
                self.bot.parse_and_send_msgs(msg, self.event.peer_id, self.event.message_thread_id)
            return [], f"{rs.title}\n\n{text}"
        else:
            raise PWarning("Я хз чё за контент")
        return attachments, rs.title

    def get_instagram_attachment(self, url):
        i_api = InstagramAPI()
        try:
            content_url = i_api.get_content_url(url)
        except (MaxRetryError, requests.exceptions.ConnectionError):
            raise PWarning("Инста забанена :(")

        if i_api.content_type == i_api.CONTENT_TYPE_IMAGE:
            return self.bot.get_photo_attachment([content_url], peer_id=self.event.peer_id), ""
        elif i_api.content_type in [i_api.CONTENT_TYPE_VIDEO, i_api.CONTENT_TYPE_REEL]:
            return self.bot.get_video_attachment(content_url, peer_id=self.event.peer_id), ""

    def get_twitter_video(self, url):
        ydl_params = {
            'outtmpl': '%(id)s%(ext)s',
            'logger': NothingLogger()
        }
        ydl = youtube_dl.YoutubeDL(ydl_params)
        ydl.add_default_info_extractors()

        try:
            video_info = ydl.extract_info(url, download=False)
        except youtube_dl.utils.DownloadError:
            raise PWarning("Не смог найти видео по этой ссылке")
        video_url = video_info['url']
        video_content = requests.get(video_url).content
        attachments = [self.bot.get_video_attachment(video_content, peer_id=self.event.peer_id)]
        return attachments, video_info['title']

    def get_pikabu_video(self, url):
        p_api = PikabuAPI()
        webm = p_api.get_video_url_from_post(url)
        video_content = requests.get(webm).content
        attachments = [
            self.bot.get_video_attachment(video_content, peer_id=self.event.peer_id, filename=p_api.filename)]
        return attachments, p_api.title

    def get_the_hole_video(self, url):
        the_hole_api = TheHoleAPI()
        the_hole_api.parse_video(url)
        attachments = [self.bot.get_document_attachment(the_hole_api.m3u8_bytes, peer_id=self.event.peer_id,
                                                        filename=f"{the_hole_api.title} - {the_hole_api.show_name} | The Hole.m3u8")]
        return attachments, f"{the_hole_api.title} | {the_hole_api.show_name}"

    def get_wasd_video(self, url):
        wasd_api = WASDAPI()
        wasd_api.parse_video_m3u8(url)
        attachments = [self.bot.get_document_attachment(wasd_api.m3u8_bytes, peer_id=self.event.peer_id,
                                                        filename=f"{wasd_api.title} - {wasd_api.show_name} | WASD.m3u8")]
        return attachments, f"{wasd_api.title} | {wasd_api.show_name}"

    def get_yandex_music(self, url):
        track = YandexMusicAPI(url)
        audiofile = track.download()
        title = f"{track.artists} - {track.title}"
        audio_att = self.bot.get_audio_attachment(audiofile, peer_id=self.event.peer_id,
                                                  filename=f"{title}.{track.format}",
                                                  thumb=track.cover_url, artist=track.artists, title=track.title)
        return [audio_att], ""

    def get_pinterest_attachment(self, url):
        p_api = PinterestAPI(url)
        content = p_api.get_attachment()
        if p_api.is_video:
            attachments = [self.bot.get_video_attachment(content, peer_id=self.event.peer_id, filename=p_api.filename)]
        elif p_api.is_image:
            attachments = [self.bot.get_photo_attachment(content, peer_id=self.event.peer_id, filename=p_api.filename)]
        elif p_api.is_gif:
            attachments = [self.bot.get_gif_attachment(content, peer_id=self.event.peer_id, filename=p_api.filename)]
        else:
            raise PWarning("Я хз чё за контент")

        return attachments, p_api.title

    def _get_file_id(self, att, _type):
        video_uploading_chat = Chat.objects.get(pk=env.str("TG_PHOTO_UPLOADING_CHAT_PK"))
        r = self.bot.parse_and_send_msgs({'attachments': [att]}, video_uploading_chat.chat_id,
                                         self.event.message_thread_id)
        r_json = r[0]['response'].json()
        self.bot.delete_message(video_uploading_chat.chat_id, r_json['result']['message_id'])
        file_id = r_json['result'][_type]['file_id']
        return file_id
