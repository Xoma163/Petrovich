from apps.bot.api.media.pinterest import Pinterest, PinterestDataItem
from apps.bot.classes.const.exceptions import PWarning
from apps.bot.commands.media.service import MediaServiceResponse, MediaService


class PinterestService(MediaService):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.service = Pinterest()

    def get_content_by_url(self, url: str) -> MediaServiceResponse:
        data: PinterestDataItem = self.service.get_post_data(url)

        if data.content_type == PinterestDataItem.CONTENT_TYPE_VIDEO:
            attachment = self.bot.get_video_attachment(data.download_url, peer_id=self.event.peer_id)
        elif data.content_type == PinterestDataItem.CONTENT_TYPE_IMAGE:
            attachment = self.bot.get_photo_attachment(data.download_url, peer_id=self.event.peer_id,
                                                       send_chat_action=False)
        elif data.content_type == PinterestDataItem.CONTENT_TYPE_GIF:
            attachment = self.bot.get_gif_attachment(data.download_url, peer_id=self.event.peer_id)
        else:
            raise PWarning(Pinterest.ERROR_MSG)

        return MediaServiceResponse(text=data.caption, attachments=[attachment])

    @classmethod
    def urls(cls) -> list[str]:
        return ['pinterest.com', 'ru.pinterest.com', 'www.pinterest.com', 'pin.it']
