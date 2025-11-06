from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import News
from articles.models import Article
from issues.models import Issue


class NewsSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.6

    def items(self):
        try:
            return News.objects.filter(is_published=True)
        except Exception:
            return []

    def location(self, obj):
        return f"/news/{obj.slug}/"


class ArticleSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        try:
            return Article.objects.filter(status='published')
        except Exception:
            return []

    def location(self, obj):
        return f"/articles/{obj.slug}/" if hasattr(obj, 'slug') and obj.slug else f"/articles/{obj.pk}/"


class IssueSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        try:
            return Issue.objects.filter(status='published')
        except Exception:
            return []

    def location(self, obj):
        return f"/issues/{obj.year}/{obj.number}/"


SITEMAPS = {
    "news": NewsSitemap,
    "articles": ArticleSitemap,
    "issues": IssueSitemap,
}


