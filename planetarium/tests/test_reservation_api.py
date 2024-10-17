from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from planetarium.models import Reservation
from planetarium.serializers import (
    ReservationListSerializer,
    ReservationRetrieveSerializer
)
from planetarium.tests.test_show_session_api import sample_session


RESERVATION_URL = reverse("planetarium:reservation-list")


def detail_url(user_id: int) -> str:
    return reverse("planetarium:reservation-detail", args=[user_id])


def sample_reservation(user: get_user_model) -> Reservation:
    return Reservation.objects.create(user=user)


class PublicReservationApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(RESERVATION_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedShowThemeApiTests(TestCase):
    def setUp(self):
        self.times = 3
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpass",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.session = sample_session()

    def test_get_reservations_list(self):
        for _ in range(self.times):
            sample_reservation(self.user)

        response = self.client.get(RESERVATION_URL)
        shows = Reservation.objects.all()
        serializer = ReservationListSerializer(shows, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)
        self.assertEqual(len(response.data["results"]), len(serializer.data))

    def test_get_reservation(self):
        reservation = sample_reservation(self.user)

        url = detail_url(reservation.id)
        response = self.client.get(url)
        serializer = ReservationRetrieveSerializer(reservation)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_post_reservation(self):
        payload = {
            "tickets": [
                {
                    "row": 1,
                    "seat": 1,
                    "show_session": self.session.id
                }
            ]
        }
        response = self.client.post(RESERVATION_URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
