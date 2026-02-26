from django.contrib import admin

# Register your models here.
from .models import SeatLock, BookingSeat, Booking, Passenger

admin.site.register(BookingSeat)
admin.site.register(SeatLock)
admin.site.register(Booking)
admin.site.register(Passenger)