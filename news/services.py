# news/services.py
from feedparser import parse
from datetime import datetime
from django.utils.timezone import now
from .models import Article



RSS_FEEDS = [
    {'url': 'https://lenta.ru/rss', 'source': 'Lenta.ru'},
    {'url': 'https://www.rbc.ru/rss/auto/topnews/', 'source': 'RBC'},
    {'url': 'https://tass.ru/rss/v2.xml', 'source': 'TASS'},
    {'url': 'https://www.kommersant.ru/RSS/news.xml', 'source': 'Kommersant'},
    {'url': 'https://www.interfax.ru/rss.asp', 'source': 'Interfax'},
    {'url': 'https://ria.ru/export/rss2/index.xml', 'source': 'RIA Novosti'},
    {'url': 'https://iz.ru/xml/rss/all.xml', 'source': 'Izvestia'},
    {'url': 'https://aif.ru/rss/news', 'source': 'AIF'},
    {'url': 'https://rg.ru/xml/rss.xml', 'source': 'RG'},
    {'url': 'https://www.vedomosti.ru/rss/rubric/business', 'source': 'Vedomosti'},
]

def extract_image_url(entry, description):
    if hasattr(entry, 'enclosures') and entry.enclosures:
        for enc in entry.enclosures:
            if enc.get('type', '').startswith('image/'):
                return enc.get('href')

    if hasattr(entry, 'media_content') and entry.media_content:
        for media in entry.media_content:
            if media.get('url'):
                return media.get('url')
    if description:
        clean_desc = unescape(description)
        match = re.search(r'<img[^>]+src=["\'](.*?)["\']', clean_desc, re.IGNORECASE)
        if match:
            return match.group(1)
    return None

def guess_category(title, description):
    text = (title + ' ' + description).lower()
    if any(word in text for word in ['технолог', 'компьютер', 'айти', 'it', 'интернет', 'софт', 'приложени', 'цифров']):
        return 'technology'
    if any(word in text for word in ['спорт', 'футбол', 'хоккей', 'теннис', 'олимпий', 'баскетбол']):
        return 'sports'
    if any(word in text for word in ['бизнес', 'экономика', 'финанс', 'рынок', 'акции', 'инвестиц', 'компани']):
        return 'business'
    if any(word in text for word in ['здоровье', 'медицина', 'больница', 'врач', 'лекарств', 'вирус']):
        return 'health'
    if any(word in text for word in ['наука', 'исследование', 'ученый', 'открытие', 'лаборатор']):
        return 'science'
    if any(word in text for word in ['кино', 'музыка', 'искусство', 'выставк', 'театр', 'культур']):
        return 'entertainment'
    return 'general'


def fetch_news_from_rss():
    articles_created = 0
    for feed_info in RSS_FEEDS:
        feed_url = feed_info['url']
        source_name = feed_info['source']
        try:
            print(f"Парсим: {source_name} - {feed_url}")
            feed = parse(feed_url)
            for entry in feed.entries:
                title = entry.get('title', '').strip()
                link = entry.get('link', '')
                if not title or not link:
                    continue
                description = entry.get('summary', '') or entry.get('description', '') or ''

                image_url = extract_image_url(entry, description)

                category = guess_category(title, description)

                published_at = now()
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    try:
                        published_at = datetime.fromtimestamp(
                            datetime.timestamp(datetime(*entry.published_parsed[:6]))
                        )
                    except:
                        pass

                _, created = Article.objects.get_or_create(
                    url=link,
                    defaults={
                        'title': title,
                        'description': description,
                        'image_url': image_url,
                        'published_at': published_at,
                        'source_name': source_name,
                        'category': category,
                    }
                )
                if created:
                    articles_created += 1
        except Exception as e:
            print(f"Ошибка с {feed_url}: {e}")
    print(f"Всего добавлено новых статей: {articles_created}")

def fetch_and_save_news():
    print("Начинаем сбор новостей из RSS...")
    fetch_news_from_rss()
    print("Готово.")