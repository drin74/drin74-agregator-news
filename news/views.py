from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Article

def news_list(request):
    articles = Article.objects.all().order_by('-published_at')
    category = request.GET.get('category')
    if category:
        articles = articles.filter(category=category)
    paginator = Paginator(articles, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'news/index.html', {'page_obj': page_obj})