from django.core.management.base import BaseCommand
from news.services import fetch_news_from_rss

class Command(BaseCommand):
    help = 'dd04a2d745cc4dbfa742e62003d5d031'

    def handle(self, *args, **kwargs):
        self.stdout.write("Обновление новостей...")
        fetch_news_from_rss()
        self.stdout.write(self.style.SUCCESS("Готово!"))