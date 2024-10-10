from rest_framework import viewsets

from planetarium.models import ShowSession, PlanetariumDome, AstronomyShow, ShowTheme, AstronomyTheme, Ticket, \
    Reservation
from planetarium.serializers import ShowSessionSerializer, PlanetariumDomeSerializer, AstronomyShowSerializer, \
    ShowThemeSerializer, AstronomyThemeSerializer, TicketSerializer, ReservationSerializer


class ShowSessionViewSet(viewsets.ModelViewSet):
    queryset = ShowSession.objects.all()
    serializer_class = ShowSessionSerializer


class PlanetariumDomeViewSet(viewsets.ModelViewSet):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializer


class AstronomyShowViewSet(viewsets.ModelViewSet):
    queryset = AstronomyShow.objects.all()
    serializer_class = AstronomyShowSerializer


class ShowThemeViewSet(viewsets.ModelViewSet):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer


class AstronomyThemeViewSet(viewsets.ModelViewSet):
    queryset = AstronomyTheme.objects.all()
    serializer_class = AstronomyThemeSerializer


class TicketThemeViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer


class ReservationThemeViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
