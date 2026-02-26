from django.conf import settings
from django.db import models
from django.utils import timezone
from apps.buses.models import Trip, Seat

import uuid



class SeatLock(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="locks")
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    expires_at = models.DateTimeField()

    class Meta:
        unique_together = ("trip", "seat")  # IMPORTANT

    def is_expired(self):
        return timezone.now() > self.expires_at
    

class Booking(models.Model):
    STATUS = [("PENDING", "Pending"), ("CONFIRMED", "Confirmed"), ("CANCELLED", "Cancelled")]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="bookings")
    pnr = models.CharField(max_length=20, unique=True, editable=False)
    status = models.CharField(max_length=10, choices=STATUS, default="PENDING")
    total_fare = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pnr:
            self.pnr = uuid.uuid4().hex[:12].upper()
        return super().save(*args, **kwargs)

class Passenger(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="passengers")
    seat = models.ForeignKey(Seat, on_delete=models.PROTECT)
    name = models.CharField(max_length=120)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10)

class BookingSeat(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="seats")
    seat = models.ForeignKey(Seat, on_delete=models.PROTECT)
    fare = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        unique_together = ("booking", "seat")
