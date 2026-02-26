from django.contrib import admin

# Register your models here.
from .models import Seat, Bus, Trip

admin.site.register(Seat)
admin.site.register(Bus)
admin.site.register(Trip)
