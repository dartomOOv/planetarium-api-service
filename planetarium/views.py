from django.db.models import Count, F
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from planetarium.mixins import QueryParamsTransform
from planetarium.models import (
    ShowSession,
    PlanetariumDome,
    AstronomyShow,
    ShowTheme,
    Reservation
)
from planetarium.serializers import (
    ShowSessionSerializer,
    PlanetariumDomeSerializer,
    AstronomyShowSerializer,
    ShowThemeSerializer,
    ReservationSerializer,
    ShowSessionListSerializer,
    ShowSessionRetrieveSerializer,
    AstronomyShowListSerializer,
    AstronomyShowRetrieveSerializer,
    PlanetariumDomeListSerializer,
    ReservationListSerializer,
    ReservationRetrieveSerializer,
)


class ShowSessionViewSet(
    QueryParamsTransform,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = ShowSession.objects.all()
    serializer_class = ShowSessionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        astronomy_shows_id = self.request.query_params.get("show")
        planetarium_domes_id = self.request.query_params.get("dome")

        if astronomy_shows_id:
            astronomy_shows_id = self.query_params_to_int(astronomy_shows_id)
            queryset = queryset.filter(astronomy_show__id__in=astronomy_shows_id)

        if planetarium_domes_id:
            planetarium_domes_id = self.query_params_to_int(planetarium_domes_id)
            queryset = queryset.filter(planetarium_dome__id__in=planetarium_domes_id)

        if self.action == "list":
            queryset = (
                queryset
                .prefetch_related("tickets")
                .annotate(available_tickets=(
                        F("planetarium_dome__rows")
                        * F("planetarium_dome__seats_in_row")
                        - Count("tickets")
                ))
            )
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return ShowSessionListSerializer
        if self.action == "retrieve":
            return ShowSessionRetrieveSerializer
        return ShowSessionSerializer


class PlanetariumDomeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return PlanetariumDomeListSerializer

        return PlanetariumDomeSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        planetarium_name = self.request.query_params.get("name")

        if planetarium_name:
            queryset = queryset.filter(name__icontains=planetarium_name)

        return queryset


class AstronomyShowViewSet(QueryParamsTransform, viewsets.ModelViewSet):
    queryset = AstronomyShow.objects.prefetch_related("themes")
    serializer_class = AstronomyShowSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return AstronomyShowListSerializer
        if self.action == "retrieve":
            return AstronomyShowRetrieveSerializer
        return AstronomyShowSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        themes_id = self.request.query_params.get("themes")
        show_title = self.request.query_params.get("title")

        if themes_id:
            themes_id = self.query_params_to_int(themes_id)
            queryset = queryset.filter(themes__pk__in=themes_id)

        if show_title:
            queryset = queryset.filter(title__icontains=show_title)

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "themes",
                type=OpenApiTypes.STR,
                description="Filter astronomy shows by title, ignoring letter case (ex. ?title=stars)",
            ),
            OpenApiParameter(
                "title",
                type=OpenApiTypes.NUMBER,
                description="Filter astronomy shows by themes ids (ex. ?themes=1,2)",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ShowThemeViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        theme_name = self.request.query_params.get("name")

        if theme_name:
            queryset = queryset.filter(name__icontains=theme_name)

        return queryset


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.prefetch_related(
        "tickets__show_session__astronomy_show"
    )
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "retrieve":
            queryset = queryset.prefetch_related(
                "tickets__show_session__planetarium_dome",
            )

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return ReservationListSerializer
        if self.action == "retrieve":
            return ReservationRetrieveSerializer
        return ReservationSerializer
