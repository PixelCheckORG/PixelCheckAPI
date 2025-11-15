from django.test import SimpleTestCase
from django.urls import resolve


class UrlsTests(SimpleTestCase):
    def test_model_health_url(self):
        resolver = resolve("/api/v1/analysis/health")
        self.assertEqual(resolver.view_name, "model-health")
        print("[Routes] /api/v1/analysis/health -> OK")
