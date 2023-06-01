from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qsl

import requests
import yt_dlp
from bs4 import BeautifulSoup

from apps.bot.classes.consts.Exceptions import PWarning, PSkip
from apps.bot.utils.NothingLogger import NothingLogger


class YoutubeVideoAPI:
    def __init__(self, max_filesize_mb=None):
        self.title = None
        self.duration = 0
        self.id = None
        self.filesize = 0
        self.filename = ""

        self.max_filesize_mb = max_filesize_mb

    @staticmethod
    def get_timecode_str(url):
        t = dict(parse_qsl(urlparse(url).query)).get('t')
        if t:
            t = t.rstrip('s')
            h, m, s = str(timedelta(seconds=int(t))).split(":")
            if h:
                return f"{h}:{m}:{s}"
            return f"{m}:{s}"
        return None

    @staticmethod
    def _clear_url(url):
        parsed = urlparse(url)
        v = dict(parse_qsl(parsed.query)).get('v')
        res = f"{parsed.scheme}://{parsed.hostname}{parsed.path}"
        if v:
            res += f"?v={v}"
        return res

    def get_last_video(self, channel_id):
        response = requests.get(f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}")
        if response.status_code != 200:
            raise PWarning("Не нашёл такого канала")
        bsop = BeautifulSoup(response.content, 'html.parser')
        last_video = bsop.find_all('entry')[0]
        link = last_video.find('link').attrs['href']
        duration = self._get_video_info(link)['duration']
        self.title = bsop.find('title').text
        return {
            'title': self.title,
            'last_video': {
                'title': last_video.find('title').text,
                'link': link,
                'date': datetime.strptime(last_video.find('published').text, '%Y-%m-%dT%H:%M:%S%z'),
                'is_shorts': duration <= 60,
            }
        }

    def _get_video_info(self, url):
        ydl_params = {
            'logger': NothingLogger()
        }
        ydl = yt_dlp.YoutubeDL(ydl_params)
        ydl.add_default_info_extractors()

        url = self._clear_url(url)
        try:
            video_info = ydl.extract_info(url, download=False)
        except yt_dlp.utils.DownloadError as e:
            if "Sign in to confirm your age" in e.msg:
                raise PWarning("К сожалению видос доступен только залогиненым пользователям")
            raise PWarning("Не смог найти видео по этой ссылке")
        return video_info

    def get_video_download_url(self, url, platform=None, timedelta=None):
        video_info = self._get_video_info(url)
        self.title = video_info['title']
        self.duration = video_info.get('duration')
        if not self.duration:
            raise PSkip()
        video_urls = [x for x in video_info['formats'] if x['ext'] == 'mp4' and x.get('asr')]
        videos = sorted(video_urls, key=lambda x: x['format_note'], reverse=True)
        if self.max_filesize_mb:  # for tg
            for video in videos:
                filesize = video.get('filesize') or video.get('filesize_approx')
                if filesize:
                    self.filesize = filesize / 1024 / 1024

                    if self.filesize < self.max_filesize_mb:
                        max_quality_video = video
                        break
                    if timedelta:
                        mbps = self.filesize / self.duration
                        if mbps * timedelta < self.max_filesize_mb - 2:
                            max_quality_video = video
                            break
            else:
                raise PSkip()
        else:
            max_quality_video = videos[0]
        self.filename = f"{self.title.replace(' ', '_')}.{max_quality_video['video_ext']}"

        url = max_quality_video['url']
        return url
