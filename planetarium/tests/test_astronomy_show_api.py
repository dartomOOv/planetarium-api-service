from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from planetarium.models import AstronomyShow
from planetarium.serializers import (
    AstronomyShowListSerializer,
    AstronomyShowRetrieveSerializer,
)
from planetarium.tests.test_show_theme_api import sample_theme


ASTRONOMY_SHOW_URL = reverse("planetarium:astronomyshow-list")
DEFAULT_PAYLOAD = {
    "title": "testtitle",
    "description": "testdesc",
}


def detail_url(show_id: int) -> str:
    return reverse("planetarium:astronomyshow-detail", args=[show_id])


def sample_show(**params) -> AstronomyShow:
    default = DEFAULT_PAYLOAD
    default.update(params)

    return AstronomyShow.objects.create(**default)


class PublicAstronomyShowApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ASTRONOMY_SHOW_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateShowThemeApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpass",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_astronomy_shows_list(self):
        sample_show()
        sample_show(title="testtitle1")

        response = self.client.get(ASTRONOMY_SHOW_URL)
        shows = AstronomyShow.objects.all()
        serializer = AstronomyShowListSerializer(shows, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)
        self.assertEqual(len(response.data["results"]), len(serializer.data))

    def test_get_planetarium_dome(self):
        show = sample_show()

        url = detail_url(show.id)
        response = self.client.get(url)
        serializer = AstronomyShowRetrieveSerializer(show)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_astronomy_shows_list_by_themes_ids(self):
        theme_1 = sample_theme(name="theme1")
        theme_2 = sample_theme(name="theme2")

        show_without_theme = sample_show()
        show_with_theme_1 = sample_show(title="testtitle2")
        show_with_theme_2 = sample_show(title="testtitle3")

        show_with_theme_1.themes.set([theme_1])
        show_with_theme_2.themes.set([theme_2])

        response = self.client.get(
            ASTRONOMY_SHOW_URL, {"themes": f"{theme_1.id},{theme_2.id}"}
        )
        serializer_without_theme = AstronomyShowListSerializer(show_without_theme)
        serializer_with_theme_1 = AstronomyShowListSerializer(show_with_theme_1)
        serializer_with_theme_2 = AstronomyShowListSerializer(show_with_theme_2)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(serializer_without_theme.data, response.data["results"])
        self.assertIn(serializer_with_theme_1.data, response.data["results"])
        self.assertIn(serializer_with_theme_2.data, response.data["results"])

    def test_get_astronomy_shows_list_by_title(self):
        show = sample_show()
        expected_show = sample_show(title="testtitle4")

        response = self.client.get(ASTRONOMY_SHOW_URL, {"title": "4"})
        serializer = AstronomyShowListSerializer(show)
        serializer_with_expected_show = AstronomyShowListSerializer(expected_show)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(serializer.data, response.data["results"])
        self.assertIn(serializer_with_expected_show.data, response.data["results"])

    def test_post_astronomy_show_forbidden(self):
        payload = DEFAULT_PAYLOAD

        response = self.client.post(ASTRONOMY_SHOW_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminShowThemeApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            email="admin@test.com",
            password="testpass",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_post_astronomy_show(self):
        theme = sample_theme()
        payload = DEFAULT_PAYLOAD.copy()
        payload.update({"themes": [f"{theme.id}"]})

        response = self.client.post(ASTRONOMY_SHOW_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
