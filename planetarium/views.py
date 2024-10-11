from rest_framework import viewsets

from planetarium.models import (
    ShowSession,
    PlanetariumDome,
    AstronomyShow,
    ShowTheme,
    AstronomyTheme,
    Ticket,
    Reservation
)
from planetarium.serializers import (
    ShowSessionSerializer,
    PlanetariumDomeSerializer,
    AstronomyShowSerializer,
    ShowThemeSerializer,
    AstronomyThemeSerializer,
    TicketSerializer,
    ReservationSerializer,
    ShowSessionListSerializer,
    ShowSessionDetailSerializer
)


class ShowSessionViewSet(viewsets.ModelViewSet):
    queryset = ShowSession.objects.all()
    serializer_class = ShowSessionSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return ShowSessionListSerializer
        if self.action == "retrieve":
            return ShowSessionDetailSerializer
        return ShowSessionSerializer



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


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
