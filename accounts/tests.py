from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

User = get_user_model()


class AuthenticationIntegrationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="A-strong-test-password-123!",
        )

    def test_dashboard_redirects_anonymous_user_to_login(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("accounts:login")))
        self.assertIn("next=%2F", response.url)

    def test_login_accepts_valid_credentials(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "testuser", "password": "A-strong-test-password-123!"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")
        self.assertIn("_auth_user_id", self.client.session)

    def test_login_rejects_external_next_url(self):
        response = self.client.post(
            reverse("accounts:login"),
            {
                "username": "testuser",
                "password": "A-strong-test-password-123!",
                "next": "https://evil.example/steal-session",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")

    def test_login_page_renders(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sign in")

    def test_logout_requires_post(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("accounts:logout"))
        self.assertEqual(response.status_code, 405)

    def test_logout_clears_session(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("accounts:logout"))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn("_auth_user_id", self.client.session)
