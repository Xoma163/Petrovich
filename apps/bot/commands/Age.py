import cv2
import numpy as np

from apps.bot.APIs.EveryPixelAPI import EveryPixelAPI
from apps.bot.classes.Command import Command
from apps.bot.classes.consts.Exceptions import PWarning
from apps.bot.classes.messages.attachments.PhotoAttachment import PhotoAttachment


class Age(Command):
    name = "возраст"
    help_text = "оценивает возраст людей на фотографии"
    help_texts = [
        "(Изображения/Пересылаемое сообщение с изображением) - оценивает возраст людей на фотографии"
    ]
    attachments = [PhotoAttachment]

    def start(self):
        image = self.event.get_all_attachments(PhotoAttachment)[0]
        everypixel_api = EveryPixelAPI()
        faces = everypixel_api.get_faces_on_photo(image.download_content())

        if len(faces) == 0:
            raise PWarning("Не нашёл лиц на фото")
        file_bytes = draw_on_images(image, faces)
        attachments = self.bot.get_photo_attachment(file_bytes, peer_id=self.event.peer_id,
                                                    filename="petrovich_age.jpg")
        return {"attachments": attachments}


def draw_on_images(image, faces):

    data = image.download_content()

    _image = np.asarray(bytearray(data), dtype="uint8")
    _image = cv2.imdecode(_image, cv2.IMREAD_COLOR)

    # B G R
    color = {'red': (0, 0, 255), 'black': (0, 0, 0), 'white': (255, 255, 255)}
    thickness = {'big': 6, 'medium': 2, 'small': 1}
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = {'big': 1, 'medium': 0.8, 'small': 0.6}
    shift_age_point = [35, 10]

    width, height, _ = _image.shape
    scale = width * height / 1920 / 1080
    scale = max(scale, 0.9)
    for x in font_scale:
        font_scale[x] *= scale
    for x in thickness:
        thickness[x] = round(thickness[x] * scale)
    for i, _ in enumerate(shift_age_point):
        shift_age_point[i] = round(shift_age_point[i] * scale)
    for face in faces:
        start_point = (int(face['bbox'][0]), int(face['bbox'][1]))
        end_point = (int(face['bbox'][2]), int(face['bbox'][3]))
        if 'age' in face:
            age = str(round(face['age']))
            age_point = (int(face['bbox'][2]) - shift_age_point[0], int(face['bbox'][3]) - shift_age_point[1])
            _image = cv2.rectangle(_image, start_point, end_point, color['red'], thickness['medium'])
            _image = cv2.putText(_image, age, age_point, font, font_scale['small'], color['black'], thickness['big'])
            _image = cv2.putText(_image, age, age_point, font, font_scale['small'], color['white'], thickness['medium'])

    _bytes = cv2.imencode('.jpg', _image)[1].tostring()
    return _bytes
