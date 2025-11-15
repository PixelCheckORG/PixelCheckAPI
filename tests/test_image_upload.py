import io
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from iam.models import User


def _fake_image_bytes() -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (16, 16), color="white").save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()


class ImageUploadTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="uploader@example.com", username="uploader", password="demo12345"
        )

    @mock.patch("ingestion.application.use_cases.run_analysis_task")
    def test_upload_enqueues_analysis(self, mock_task):
        self.client.force_authenticate(self.user)
        file = SimpleUploadedFile(
            "sample.png",
            _fake_image_bytes(),
            content_type="image/png",
        )
        response = self.client.post(reverse("upload-image"), {"image": file}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn("imageId", response.data)
        mock_task.delay.assert_called_once()
        print("[Ingestion] Upload + Celery enqueue -> OK")
