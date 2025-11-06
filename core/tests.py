from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from core.models import News


class UrlsSmokeTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Данные для новостей
        self.news = News.objects.create(title='Demo', slug='demo', content='x', is_published=True, published_at=timezone.now())

    def test_healthz(self):
        resp = self.client.get('/healthz')
        self.assertEqual(resp.status_code, 200)
        self.assertJSONEqual(resp.content, {"status": "ok"})

    def test_news_list_and_detail(self):
        self.assertEqual(self.client.get(reverse('core:news_list')).status_code, 200)
        self.assertEqual(self.client.get(reverse('core:news_detail', kwargs={'slug': 'demo'})).status_code, 200)

    def test_search_page(self):
        self.assertEqual(self.client.get(reverse('core:search'), {'q': 'Demo'}).status_code, 200)

    def test_api_search(self):
        r = self.client.get(reverse('core:api_search'), {'q': 'Demo'})
        self.assertEqual(r.status_code, 200)
        self.assertIn('results', r.json())

    def test_sitemap(self):
        r = self.client.get('/sitemap.xml')
        self.assertEqual(r.status_code, 200)
        self.assertIn(b'<urlset', r.content)

# Create your tests here.
