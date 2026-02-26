from django.urls import path
from .views import search_view, trips_list_view
from apps.bookings.views import select_seats_view

urlpatterns = [
    path("", search_view, name="search"),
    path("trips/", trips_list_view, name="trips_list"),
    path("trips/<int:trip_id>/seats/", select_seats_view, name="select_seats"),
]