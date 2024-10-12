from django.urls import path, include
from rest_framework import routers

from planetarium.views import (
    AstronomyShowViewSet,
    ShowSessionViewSet,
    PlanetariumDomeViewSet,
    ReservationViewSet,
    ShowThemeViewSet,
    TicketViewSet,
)


router = routers.DefaultRouter()

router.register("show-sessions", ShowSessionViewSet)
router.register("planetarium-domes", PlanetariumDomeViewSet)
router.register("astronomy-shows", AstronomyShowViewSet)
router.register("show-themes", ShowThemeViewSet)
router.register("tickets", TicketViewSet)
router.register("reservations", ReservationViewSet)

app_name = "planetarium"

urlpatterns = [
    path("", include(router.urls))
]
