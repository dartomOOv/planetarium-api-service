from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from planetarium.models import ShowTheme
from planetarium.serializers import ShowThemeSerializer


SHOW_THEME_URL = reverse("planetarium:showtheme-list")


def sample_theme(**params) -> ShowTheme:
    default = {"name": "testtheme"}
    default.update(params)

    return ShowTheme.objects.create(**default)


class PublicShowSessionApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(SHOW_THEME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateShowThemeApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpass",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_show_themes_list(self):
        sample_theme()
        sample_theme(name="testtheme1")

        response = self.client.get(SHOW_THEME_URL)
        themes = ShowTheme.objects.all()
        serializer = ShowThemeSerializer(themes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)
        self.assertEqual(len(response.data["results"]), len(serializer.data))

    def test_get_show_themes_list_by_name(self):
        theme_1 = sample_theme()
        expected_theme = sample_theme(name="testtheme1")

        response = self.client.get(SHOW_THEME_URL, {"name": "1"})
        serializer_1 = ShowThemeSerializer(theme_1)
        serializer_with_expected_theme = ShowThemeSerializer(expected_theme)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(serializer_1.data, response.data["results"])
        self.assertIn(serializer_with_expected_theme.data, response.data["results"])

    def test_post_show_theme_forbidden(self):
        payload = {"name": "testpost"}

        response = self.client.post(SHOW_THEME_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
