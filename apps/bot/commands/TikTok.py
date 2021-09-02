import json
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from apps.bot.classes.Consts import Platform
from apps.bot.classes.Exceptions import PWarning
from apps.bot.classes.common.CommonCommand import CommonCommand

TIKTOK_URLS = ["www.tiktok.com", 'vm.tiktok.com']


class TikTok(CommonCommand):
    name = "тикток"
    names = ["TikTok"]
    help_text = "присылает видео с тиктока"
    help_texts = ["(ссылка на тикток) - присылает видео с тиктока"]
    platforms = [Platform.TG]

    def accept(self, event):
        if urlparse(event.command).hostname in TIKTOK_URLS:
            return True
        if event.fwd:
            if urlparse(event.fwd[0]['text']).hostname in TIKTOK_URLS:
                return True
        return super().accept(event)

    def start(self):
        if self.event.command in self.full_names:
            if self.event.args:
                url = self.event.args[0]
            elif self.event.fwd:
                url = self.event.fwd[0]['text']
            else:
                raise PWarning("Для работы команды требуются аргументы или пересылаемые сообщения")
        else:
            url = self.event.clear_msg

        if urlparse(url).hostname not in TIKTOK_URLS:
            raise PWarning("Не TikTok ссылка")

        self.bot.set_activity(self.event.peer_id, 'typing')
        if self.event.command not in self.full_names:
            try:
                video = self.get_video_by_url(url)
            except:
                return
        else:
            video = self.get_video_by_url(url)

        attachments = [self.bot.upload_video(video)]
        return {
            'attachments': attachments
        }

    def get_video_by_url(self, url):
        print(url)
        headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

        s = requests.Session()
        r = s.get(url, headers=headers)
        # ToDo: just regexp
        bs4 = BeautifulSoup(r.content, 'html.parser')
        video_data = json.loads(bs4.find(id='__NEXT_DATA__').contents[0])

        video_url = video_data['props']['pageProps']['itemInfo']['itemStruct']['video']['downloadAddr']

        headers['Referer'] = video_data['props']['pageProps']['seoProps']['metaParams']['canonicalHref']
        # return video_url
        r = s.get(video_url, headers=headers)
        s.close()
        return r.content