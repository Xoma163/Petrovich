import io
from io import BytesIO

from PIL import Image

from apps.bot.classes.Command import Command
from apps.bot.classes.messages.attachments.PhotoAttachment import PhotoAttachment
from apps.bot.utils.Demotivator import DemotivatorBuilder
from apps.bot.utils.utils import get_attachments_from_attachments_or_fwd


class Demotivator(Command):
    name = "демотиватор"
    help_text = "создаёт демотиватор"
    help_texts = [
        "(Изображения/Пересылаемое сообщение с изображением) (большой текст)[;маленький текст] - создаёт демотиватор\n"
        "Разделитель текста ;"
    ]
    args = 1
    attachments = [PhotoAttachment]

    def start(self):
        image = get_attachments_from_attachments_or_fwd(self.event, PhotoAttachment)[0]

        texts = list(map(str.strip, self.event.message.args_str.split(';')))
        if not texts[0]:
            return "Первая фраза обязательно должна быть"

        content = image.download_content()
        base_image = Image.open(BytesIO(content))
        db = DemotivatorBuilder(base_image, *texts)
        demotivator = db.get_demotivator()
        img_byte_arr = io.BytesIO()
        demotivator.save(img_byte_arr, format="PNG")

        attachments = self.bot.upload_photos(img_byte_arr)
        return {"attachments": attachments}
