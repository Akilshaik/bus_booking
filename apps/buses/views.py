# buses/views.py
from django.shortcuts import render
from django.utils.dateparse import parse_date
from apps.core.models import City, Route
from .models import Trip
from datetime import timedelta
from django.utils import timezone


def search_view(request):
    cities = City.objects.all().order_by("name")
    return render(request, "buses/search.html", {"cities": cities})



def trips_list_view(request):
    source_id = request.GET.get("source")
    dest_id = request.GET.get("destination")
    date_str = (request.GET.get("date") or "").strip()

    trips = Trip.objects.none()

    # If route not selected, show empty results
    if not (source_id and dest_id):
        return render(request, "buses/trips_list.html", {"trips": trips})

    route = Route.objects.filter(source_id=source_id, destination_id=dest_id).first()
    if not route:
        return render(request, "buses/trips_list.html", {"trips": trips})

    # If date is provided, use it; otherwise use today..today+7days
    journey_date = parse_date(date_str) if date_str else None

    qs = (
        Trip.objects.filter(route=route, active=True)
        .select_related("bus", "route", "route__source", "route__destination")
        .order_by("journey_date", "departure_time")
    )

    if journey_date:
        # Existing behavior: single date
        trips = qs.filter(journey_date=today)
    else:
        # New behavior: today -> next 7 days
        today = timezone.localdate()
        end_date = today + timedelta(days=7)
        trips = qs.filter(journey_date__range=(today, end_date))

    return render(request, "buses/trips_list.html", {"trips": trips})
