from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from planetarium.models import ShowSession
from planetarium.serializers import (
    ShowSessionListSerializer,
    ShowSessionRetrieveSerializer,
)
from planetarium.tests.test_astronomy_show_api import sample_show
from planetarium.tests.test_planetarium_dome_api import sample_dome


SHOW_SESSION_URL = reverse("planetarium:showsession-list")


def detail_url(session_id: int) -> str:
    return reverse("planetarium:showsession-detail", args=[session_id])


def sample_session(**params) -> ShowSession:
    show = sample_show()
    dome = sample_dome()
    default = {
        "astronomy_show": show,
        "planetarium_dome": dome,
        "show_time": datetime.now(),
    }
    default.update(params)

    session = ShowSession.objects.create(**default)
    session.available_tickets = (
        session.planetarium_dome.total_seats - session.tickets.count()
    )

    return session


def set_available_tickets_field(show_session: ShowSession) -> None:
    show_session.available_tickets = (
        show_session.planetarium_dome.total_seats - show_session.tickets.count()
    )


class PublicShowSessionApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(SHOW_SESSION_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateShowSessionApiTests(TestCase):
    def setUp(self):
        self.show = sample_show()
        self.dome = sample_dome()
        self.show_session = ShowSession.objects.create(
            astronomy_show=self.show,
            planetarium_dome=self.dome,
            show_time=datetime.now(),
        )
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpass",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_show_session_list(self):
        response = self.client.get(SHOW_SESSION_URL)
        sessions = ShowSession.objects.all()
        for session in sessions:
            set_available_tickets_field(session)
        serializer = ShowSessionListSerializer(sessions, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), len(serializer.data))
        for data in serializer.data:
            self.assertIn(data, response.data["results"])

    def test_get_show_session(self):
        url = detail_url(self.show_session.id)
        response = self.client.get(url)
        serializer = ShowSessionRetrieveSerializer(self.show_session)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_show_sessions_list_by_astronomy_shows_ids(self):
        session_with_show_1 = ShowSession.objects.create(
            astronomy_show=sample_show(title="testshow1"),
            planetarium_dome=self.dome,
            show_time=datetime.now(),
        )
        session_with_show_2 = ShowSession.objects.create(
            astronomy_show=sample_show(title="testshow2"),
            planetarium_dome=self.dome,
            show_time=datetime.now(),
        )
        set_available_tickets_field(session_with_show_1)
        set_available_tickets_field(session_with_show_2)

        response = self.client.get(
            SHOW_SESSION_URL,
            {
                "show": (
                    f"{session_with_show_1.astronomy_show.id},"
                    f"{session_with_show_2.astronomy_show.id}"
                )
            },
        )
        default_serializer = ShowSessionListSerializer(self.show_session)
        serializer_with_show_1 = ShowSessionListSerializer(session_with_show_1)
        serializer_with_show_2 = ShowSessionListSerializer(session_with_show_2)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(default_serializer.data, response.data["results"])
        self.assertIn(serializer_with_show_1.data, response.data["results"])
        self.assertIn(serializer_with_show_2.data, response.data["results"])

    def test_get_show_sessions_list_by_planetarium_domes_ids(self):
        dome = sample_dome(name="testname1")

        session_with_dome_1 = ShowSession.objects.create(
            astronomy_show=sample_show(title="testshow3"),
            planetarium_dome=dome,
            show_time=datetime.now(),
        )
        session_with_dome_2 = ShowSession.objects.create(
            astronomy_show=sample_show(title="testshow4"),
            planetarium_dome=dome,
            show_time=datetime.now(),
        )

        set_available_tickets_field(session_with_dome_1)
        set_available_tickets_field(session_with_dome_2)

        response = self.client.get(
            SHOW_SESSION_URL, {"dome": (f"{session_with_dome_1.planetarium_dome.pk}")}
        )

        default_serializer = ShowSessionListSerializer(self.show_session)
        serializer_with_dome_1 = ShowSessionListSerializer(session_with_dome_1)
        serializer_with_dome_2 = ShowSessionListSerializer(session_with_dome_2)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(default_serializer.data, response.data["results"])
        self.assertIn(serializer_with_dome_1.data, response.data["results"])
        self.assertIn(serializer_with_dome_2.data, response.data["results"])

    def test_post_astronomy_show_forbidden(self):
        payload = {
            "astronomy_show": sample_show(title="forbidden"),
            "planetarium_dome": sample_dome(),
            "show_time": datetime.now(),
        }

        response = self.client.post(SHOW_SESSION_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminShowThemeApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            email="admin@test.com",
            password="testpass",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_post_show_sessions(self):
        payload = {
            "astronomy_show": sample_show(title="allowed").id,
            "planetarium_dome": sample_dome().id,
            "show_time": datetime.now(),
        }

        response = self.client.post(SHOW_SESSION_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
