# buses/views.py
from django.shortcuts import render
from django.utils.dateparse import parse_date
from apps.core.models import City, Route
from .models import Trip

def search_view(request):
    cities = City.objects.all().order_by("name")
    return render(request, "buses/search.html", {"cities": cities})


def trips_list_view(request):
    source_id = request.GET.get("source")
    dest_id = request.GET.get("destination")
    date_str = request.GET.get("date")

    trips = Trip.objects.none()

    if source_id and dest_id and date_str:
        journey_date = parse_date(date_str)
        route = Route.objects.filter(source_id=source_id, destination_id=dest_id).first()
        if route and journey_date:
            trips = (
                Trip.objects.filter(route=route, journey_date=journey_date, active=True)
                .select_related("bus", "route", "route__source", "route__destination")
                .order_by("departure_time")
            )

    return render(request, "buses/trips_list.html", {"trips": trips})