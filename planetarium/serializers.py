from rest_framework import serializers

from planetarium.models import (
    ShowSession,
    PlanetariumDome,
    AstronomyShow,
    ShowTheme,
    Ticket,
    Reservation
)


class PlanetariumDomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanetariumDome
        fields = ["id", "name", "rows", "seats_in_row"]


class PlanetariumDomeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanetariumDome
        fields = ["id", "name", "total_seats"]


class ShowThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowTheme
        fields = ["id", "name"]


class AstronomyShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = AstronomyShow
        fields = ["id", "title", "description", "themes"]


class AstronomyShowListSerializer(AstronomyShowSerializer):
    themes = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name"
    )


class AstronomyShowRetrieveSerializer(AstronomyShowSerializer):
    themes = ShowThemeSerializer(many=True)


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["id", "row", "seat", "show_session"]

    def validate(self, attrs):
        Ticket.validate_seat_row(
            attrs["row"],
            attrs["seat"],
            attrs["show_session"].planetarium_dome,
        )
        return attrs


class TicketListSerializer(TicketSerializer):
    show_session = serializers.SlugRelatedField(
        read_only=True,
        slug_field="astronomy_show.title",
    )


class ShowSessionTicketSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ["seat", "row"]


class ShowSessionSerializer(serializers.ModelSerializer):
    available_tickets = serializers.IntegerField(read_only=True)

    class Meta:
        model = ShowSession
        fields = ["id", "astronomy_show", "planetarium_dome", "show_time", "available_tickets"]


class ShowSessionListSerializer(ShowSessionSerializer):
    astronomy_show = serializers.SlugRelatedField(slug_field="title", read_only=True)
    planetarium_dome = serializers.SlugRelatedField(slug_field="name", read_only=True)


class ShowSessionRetrieveSerializer(ShowSessionSerializer):
    astronomy_show = AstronomyShowListSerializer()
    planetarium_dome = serializers.SlugRelatedField(
        read_only=True,
        slug_field="name"
    )
    taken_tickets = ShowSessionTicketSerializer(many=True, source="tickets")

    class Meta:
        model = ShowSession
        fields = ShowSessionSerializer.Meta.fields + ["taken_tickets"]


class TicketRetrieveSerializer(TicketListSerializer):
    show_session = ShowSessionListSerializer()


class ReservationSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True)

    class Meta:
        model = Reservation
        fields = ["id", "created_at", "tickets"]

    def create(self, validated_data):
        tickets = validated_data.pop("tickets")
        reservation = Reservation.objects.create(**validated_data)
        for ticket in tickets:
            Ticket.objects.create(reservation=reservation, **ticket)
        return reservation


class ReservationListSerializer(ReservationSerializer):
    tickets = TicketListSerializer(many=True)


class ReservationRetrieveSerializer(ReservationSerializer):
    tickets = TicketRetrieveSerializer(many=True)
