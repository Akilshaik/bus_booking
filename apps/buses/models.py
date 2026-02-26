from django.db import models
from apps.core.models import Route

class Bus(models.Model):
    BUS_TYPES = [
        ("AC_SEATER", "AC Seater"),
        ("NONAC_SEATER", "Non-AC Seater"),
        ("AC_SLEEPER", "AC Sleeper"),
        ("NONAC_SLEEPER", "Non-AC Sleeper"),
    ]
    operator_name = models.CharField(max_length=150)
    bus_number = models.CharField(max_length=50, unique=True)
    bus_type = models.CharField(max_length=20, choices=BUS_TYPES)
    total_seats = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.operator_name} ({self.bus_number})"

class Seat(models.Model):
    SEAT_TYPES = [("SEATER", "Seater"), ("SLEEPER", "Sleeper")]
    DECKS = [("LOWER", "Lower"), ("UPPER", "Upper")]

    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name="seats")
    seat_number = models.CharField(max_length=10)  # e.g. A1, A2, U1
    seat_type = models.CharField(max_length=10, choices=SEAT_TYPES)
    deck = models.CharField(max_length=10, choices=DECKS, default="LOWER")
    row = models.PositiveIntegerField()
    col = models.PositiveIntegerField()

    class Meta:
        unique_together = ("bus", "seat_number")

    def __str__(self):
        return f"{self.bus.bus_number} - {self.seat_number}"

class Trip(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name="trips")
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="trips")
    journey_date = models.DateField()
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    base_fare = models.DecimalField(max_digits=8, decimal_places=2)
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("bus", "journey_date", "departure_time")

    def __str__(self):
        return f"{self.route} on {self.journey_date} ({self.bus.bus_number})"
