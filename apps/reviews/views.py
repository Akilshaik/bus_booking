# reviews/views.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg, Count
from django.shortcuts import get_object_or_404, redirect, render

from apps.buses.models import Bus
from apps.bookings.models import Booking
from .models import Review


def bus_select(request):
    q = request.GET.get("q", "").strip()

    buses = Bus.objects.all().order_by("operator_name", "bus_number")

    if q:
        buses = buses.filter(
            Q(operator_name__icontains=q) |
            Q(bus_number__icontains=q) |
            Q(bus_type__icontains=q)
        )

    return render(request, "reviews/bus_select.html", {"buses": buses})


def bus_reviews_view(request, bus_id):
    bus = get_object_or_404(Bus, id=bus_id)

    reviews = (
        Review.objects.filter(bus=bus)
        .select_related("user")
        .order_by("-created_at")
    )

    stats = reviews.aggregate(avg=Avg("rating"), total=Count("id"))
    average_rating = round(stats["avg"] or 0, 1)
    total_reviews = stats["total"] or 0

    return render(
        request,
        "reviews/bus_reviews.html",
        {
            "bus": bus,
            "reviews": reviews,
            "average_rating": average_rating,
            "total_reviews": total_reviews,
        },
    )


@login_required
def add_review_view(request, bus_id):
    bus = get_object_or_404(Bus, id=bus_id)

    # Optional rule: allow review only if user has a confirmed booking on this bus
    has_booking = Booking.objects.filter(
        user=request.user,
        trip__bus=bus,
        status="CONFIRMED"
    ).exists()

    if not has_booking:
        messages.error(request, "You can review only after a confirmed booking.")
        return redirect("bus_reviews", bus_id=bus.id)

    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment", "").strip()

        if not rating:
            messages.error(request, "Rating is required.")
            return redirect("add_review", bus_id=bus.id)

        Review.objects.update_or_create(
            user=request.user,
            bus=bus,
            defaults={"rating": int(rating), "comment": comment},
        )

        messages.success(request, "Review submitted.")
        return redirect("bus_reviews", bus_id=bus.id)

    return render(request, "reviews/add_review.html", {"bus": bus})
