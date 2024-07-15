import datetime

from django.core.management.base import BaseCommand

from apps.service.models import VideoCache


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.delete_video_caches()

    @staticmethod
    def delete_video_caches():
        DAYS = 30
        dt = datetime.datetime.now().date() - datetime.timedelta(days=DAYS)
        VideoCache.objects.filter(created_at__lte=dt).delete()
