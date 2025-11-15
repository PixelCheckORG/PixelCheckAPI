from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from analysis.models import AnalysisResult
from iam.models import User
from ingestion.models import Image


class ResultsEndpointTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com", username="owner", password="demo1234"
        )
        self.client.force_authenticate(self.owner)
        self.image = Image.objects.create(
            uploader=self.owner,
            filename="test.png",
            mime_type="image/png",
            size_bytes=10,
            width=1,
            height=1,
            checksum="abc123",
            status=Image.Status.DONE,
        )
        AnalysisResult.objects.create(
            image=self.image,
            owner=self.owner,
            label=AnalysisResult.Label.REAL,
            confidence=0.85,
            model_version="v1",
        )

    def test_retrieve_result(self):
        response = self.client.get(reverse("result-detail", args=[self.image.image_id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["label"], "REAL")
        self.assertEqual(response.data["modelVersion"], "v1")
        print("[Results] Consulta de resultado -> OK")
