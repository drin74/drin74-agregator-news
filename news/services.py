import requests
from datetime import datetime
from django.utils.timezone import now
from .models import Article

# ========== НАСТРОЙКИ GNEWS ==========
# Сюда вы вставите ваш рабочий API-ключ, который получите на сайте GNews.
GNEWS_API_KEY = 'dd04a2d745cc4dbfa742e62003d5d031'
GNEWS_API_ENDPOINT = 'https://gnews.io/api/v4/top-headlines'

# Это наша основная функция для загрузки новостей из GNews.
# Она принимает параметр `category`.
def fetch_news_from_gnews(category='general'):
    """
    Загружает новости из GNews API и сохраняет их в базу данных.
    """
    headers = {
        # GNews ожидает ключ в параметре apikey, мы добавим его чуть позже.
    }
    params = {
        'country': 'ru',        # Фильтруем по стране Россия
        'category': category,   # Категория новостей
        'apikey': GNEWS_API_KEY, # Ваш API-ключ
        'max': 50,              # Количество статей (от 1 до 100)
        'lang': 'ru',
    }
    try:
        response = requests.get(GNEWS_API_ENDPOINT, params=params)
        if response.status_code == 200:
            data = response.json()
            articles_data = data.get('articles', [])
            articles_created = 0
            for item in articles_data:
                title = item.get('title')
                if not title:
                    continue
                url = item.get('url')
                if not url:
                    continue
                description = item.get('description') or ''
                image_url = item.get('image') or None
                source_name = item.get('source', {}).get('name') or 'Unknown'

                # Обработка даты публикации
                published_at = None
                published_at_str = item.get('publishedAt')
                if published_at_str:
                    try:
                        published_at = datetime.fromisoformat(published_at_str.replace('Z', '+00:00'))
                    except ValueError:
                        pass
                if published_at is None:
                    published_at = now()

                # Используем get_or_create, чтобы избежать дублирования по URL
                _, created = Article.objects.get_or_create(
                    url=url,
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
            print(f"Сохранено новых статей для категории '{category}': {articles_created}")
        else:
            print(f"Ошибка запроса к GNews API: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Произошла ошибка при загрузке новостей: {e}")
