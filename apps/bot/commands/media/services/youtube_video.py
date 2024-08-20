from apps.bot.api.media.youtube.video import YoutubeVideo
from apps.bot.classes.bots.chat_activity import ChatActivity
from apps.bot.classes.const.activities import ActivitiesEnum
from apps.bot.commands.media.service import MediaService, MediaServiceResponse
from apps.bot.utils.utils import retry


class YoutubeVideoService(MediaService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.use_proxy = True
        self.service = YoutubeVideo(use_proxy=self.use_proxy)

    @retry(3, Exception, sleep_time=2)
    def get_content_by_url(self, url: str) -> MediaServiceResponse:
        with ChatActivity(self.bot, ActivitiesEnum.UPLOAD_VIDEO, self.event.peer_id):
            return self._get_content_by_url(url)

    def _get_content_by_url(self, url: str) -> MediaServiceResponse:
        high_res = self.HIGH_KEYS.intersection(self.event.message.keys)
        data = self.service.get_video_info(url, high_res=high_res)
        text = data.title if data.duration > 60 else None

        if cached := self._get_cached(data.channel_id, data.video_id, text):
            return cached

        va = self.service.download_video(data)

        if va.get_size_mb() > self.bot.MAX_VIDEO_SIZE_MB:
            return self._cache_video(data.channel_id, data.video_id, data.title, va.content)

        return MediaServiceResponse(text=text, attachments=[va], video_title=data.title)

    def check_valid_url(self, url: str) -> None:
        self.service.check_url_is_video(url)

    @classmethod
    def urls(cls) -> list[str]:
        return ['www.youtube.com', 'youtube.com', "www.youtu.be", "youtu.be", "m.youtube.com"]