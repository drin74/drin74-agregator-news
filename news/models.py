from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    url = models.URLField(unique=True)
    image_url = models.URLField(blank=True, null=True)
    published_at = models.DateTimeField(null=True, blank=True)
    source_name = models.CharField(max_length=200)
    category = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.title