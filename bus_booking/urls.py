from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.buses.urls")),
    path("bookings/", include("apps.bookings.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("reviews/", include("apps.reviews.urls")),
]