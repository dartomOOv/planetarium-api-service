from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


from rest_framework import status
from rest_framework.test import APIClient

from planetarium.models import PlanetariumDome
from planetarium.serializers import (
    PlanetariumDomeSerializer,
    PlanetariumDomeListSerializer,
)

PLANETARIUM_DOME_URL = reverse("planetarium:planetariumdome-list")


def detail_url(dome_id: int) -> str:
    return reverse("planetarium:planetariumdome-detail", args=[dome_id])


def sample_dome(**params) -> PlanetariumDome:
    default = {"name": "testdome", "rows": 5, "seats_in_row": 6}
    default.update(params)

    return PlanetariumDome.objects.create(**default)


class PublicPlanetariumDomeApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(PLANETARIUM_DOME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivatePlanetariumDomeApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpass",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_planetarium_domes_list(self):
        sample_dome()
        sample_dome(name="testdome1")

        response = self.client.get(PLANETARIUM_DOME_URL)
        domes = PlanetariumDome.objects.all()
        serializer = PlanetariumDomeListSerializer(domes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)
        self.assertEqual(len(response.data["results"]), len(serializer.data))

    def test_get_planetarium_dome(self):
        dome = sample_dome()

        url = detail_url(dome.id)
        response = self.client.get(url)
        serializer = PlanetariumDomeSerializer(dome)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_planetarium_domes_list_by_name(self):
        dome_1 = sample_dome()
        expected_dome = sample_dome(name="testdome1")

        response = self.client.get(PLANETARIUM_DOME_URL, {"name": "1"})
        serializer_1 = PlanetariumDomeListSerializer(dome_1)
        serializer_with_expected_dome = PlanetariumDomeListSerializer(expected_dome)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(serializer_1.data, response.data["results"])
        self.assertIn(serializer_with_expected_dome.data, response.data["results"])
