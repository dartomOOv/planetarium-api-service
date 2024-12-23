from django.db.models import Count, F

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter

from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from planetarium.mixins import QueryParamsTransform
from planetarium.models import (
    AstronomyShow,
    PlanetariumDome,
    Reservation,
    ShowSession,
    ShowTheme
)
from planetarium.serializers import (
    AstronomyShowSerializer,
    AstronomyShowListSerializer,
    AstronomyShowRetrieveSerializer,
    PlanetariumDomeSerializer,
    PlanetariumDomeListSerializer,
    ReservationSerializer,
    ReservationListSerializer,
    ReservationRetrieveSerializer,
    ShowSessionSerializer,
    ShowSessionListSerializer,
    ShowSessionRetrieveSerializer,
    ShowThemeSerializer,
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
        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return ShowSessionListSerializer
        if self.action == "retrieve":
            return ShowSessionRetrieveSerializer
        return self.serializer_class

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "show",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter show sessions by astronomy shows id (ex. ?show=1,2)",
            ),
            OpenApiParameter(
                "dome",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter show sessions by planetarium domes id (ex. ?dome=1,2)",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class PlanetariumDomeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return PlanetariumDomeListSerializer

        return self.serializer_class

    def get_queryset(self):
        queryset = super().get_queryset()
        planetarium_name = self.request.query_params.get("name")

        if planetarium_name:
            queryset = queryset.filter(name__icontains=planetarium_name)

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "name",
                type=OpenApiTypes.STR,
                description="Filter planetarium domes by name, ignoring letter case (ex. ?name=main)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class AstronomyShowViewSet(QueryParamsTransform, viewsets.ModelViewSet):
    queryset = AstronomyShow.objects.prefetch_related("themes")
    serializer_class = AstronomyShowSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return AstronomyShowListSerializer
        if self.action == "retrieve":
            return AstronomyShowRetrieveSerializer
        return self.serializer_class

    def get_queryset(self):
        queryset = super().get_queryset()
        themes_id = self.request.query_params.get("themes")
        show_title = self.request.query_params.get("title")

        if themes_id:
            themes_id = self.query_params_to_int(themes_id)
            queryset = queryset.filter(themes__pk__in=themes_id)

        if show_title:
            queryset = queryset.filter(title__icontains=show_title)

        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "themes",
                type=OpenApiTypes.STR,
                description="Filter astronomy shows by title, ignoring letter case (ex. ?title=stars)",
            ),
            OpenApiParameter(
                "title",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter astronomy shows by themes id (ex. ?themes=1,2)",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ShowThemeViewSet(
    mixins.ListModelMixin,
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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "name",
                type=OpenApiTypes.STR,
                description="Filter themes by name, ignoring letter case (ex. ?name=space)",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ReservationViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Reservation.objects.prefetch_related(
        "tickets__show_session__astronomy_show"
    )
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)

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
        return self.serializer_class
