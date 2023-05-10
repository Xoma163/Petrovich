import time

from django.core.management import BaseCommand

from apps.bot.classes.bots.tg.TgBot import TgBot
from apps.service.models import Meme


class Command(BaseCommand):
    pass

    def handle(self, *args, **options):
        memes = Meme.objects.filter(type__in=['photo'], tg_file_id="")
        tg_bot = TgBot()

        for i, meme in enumerate(memes):
            print(f"{i}/{len(memes)}")
            try:
                photo = tg_bot.upload_image_to_tg_server(meme.link)
            except:
                continue
            meme.tg_file_id = photo.file_id
            meme.save()

            time.sleep(2)
