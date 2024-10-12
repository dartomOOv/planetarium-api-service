from django.core.exceptions import ValidationError
from django.db import models

from config.settings import AUTH_USER_MODEL


class ShowSession(models.Model):
    astronomy_show = models.ForeignKey(to="AstronomyShow", on_delete=models.CASCADE, related_name="sessions")
    planetarium_dome = models.ForeignKey(to="PlanetariumDome", on_delete=models.CASCADE, related_name="sessions")
    show_time = models.DateTimeField()

    def __str__(self):
        return f"{self.astronomy_show.title} in {self.planetarium_dome.name} Dome at {self.show_time}"


class PlanetariumDome(models.Model):
    name = models.CharField(max_length=128)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()

    def __str__(self):
        return f"{self.name} (rows: {self.rows}, seats in row: {self.seats_in_row})"


class AstronomyShow(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    themes = models.ManyToManyField(to="ShowTheme", related_name="astronomy_shows")

    def __str__(self):
        return self.title


class ShowTheme(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    show_session = models.ForeignKey(to="ShowSession", on_delete=models.CASCADE, related_name="tickets")
    reservation = models.ForeignKey(to="Reservation", on_delete=models.CASCADE, related_name="tickets")

    def __str__(self):
        return f"Ticket: row - {self.row}, seat - {self.seat} ({self.show_session.astronomy_show.title})"

    @staticmethod
    def validate_seat_row(
        row: int,
        seat: int,
        planetarium_dome: PlanetariumDome
    ):
        for ticket_attr_value, ticket_attr_name, dome_attr_name in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row"),
        ]:
            count_attrs = getattr(planetarium_dome, dome_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise ValidationError(
                    f"{ticket_attr_name} "
                    "number must be in available range: "
                    f"(1, {dome_attr_name}): "
                    f"(1, {count_attrs})"
                )

    def clean(self):
        Ticket.validate_seat_row(
            row=self.row,
            seat=self.seat,
            planetarium_dome=self.show_session.planetarium_dome
        )


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(to=AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reservations")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return str(self.created_at)
