from django.contrib import admin

# Register your models here.
from .models import City, Route

admin.site.register(City)
admin.site.register(Route)