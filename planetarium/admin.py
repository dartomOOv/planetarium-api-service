from django.contrib import admin

from planetarium.models import (
    AstronomyShow,
    AstronomyTheme,
    Reservation,
    PlanetariumDome,
    ShowSession,
    ShowTheme,
    Ticket,
)


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 1


@admin.register(Reservation)
class OrderAdmin(admin.ModelAdmin):
    inlines = [TicketInline]


admin.site.register(ShowSession)
admin.site.register(PlanetariumDome)
admin.site.register(AstronomyShow)
admin.site.register(ShowTheme)
admin.site.register(AstronomyTheme)
admin.site.register(Ticket)
