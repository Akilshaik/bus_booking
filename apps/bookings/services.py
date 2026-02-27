from django.utils import timezone
from .models import SeatLock, BookingSeat

def get_unavailable_seat_ids(trip):
    """
    Unavailable = (locked and not expired) OR (already booked in confirmed booking).
    """
    now = timezone.now()

    locked_ids = SeatLock.objects.filter(
        trip=trip, expires_at__gt=now
    ).values_list("seat_id", flat=True)

    booked_ids = BookingSeat.objects.filter(
        booking__trip=trip,
        booking__status="CONFIRMED"
    ).values_list("seat_id", flat=True)

    return set(locked_ids) | set(booked_ids)