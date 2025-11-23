from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class AuthFlowTests(APITestCase):
    def test_sign_up_and_sign_in(self):
        payload = {
            "username": "demo",
            "password": "supersecret123",
            "roles": ["ROLE_USER"],
        }
        response = self.client.post(reverse("sign-up"), payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("userId", response.data)

        signin_response = self.client.post(
            reverse("sign-in"),
            {
                "username": payload["username"],
                "password": payload["password"],
            },
        )
        self.assertEqual(signin_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", signin_response.data)
        print("[Auth] Registro + login JWT -> OK")
