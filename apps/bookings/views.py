from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction, IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import HttpResponse, Http404
from django.template.loader import render_to_string

from apps.buses.models import Trip, Seat
from .models import SeatLock, Booking, BookingSeat, Passenger
from .services import get_unavailable_seat_ids

LOCK_MINUTES = 8


@login_required
def select_seats_view(request, trip_id):
    trip = get_object_or_404(
        Trip.objects.select_related("bus", "route", "route__source", "route__destination"),
        id=trip_id, active=True
    )

    seats = Seat.objects.filter(bus=trip.bus).order_by("deck", "row", "col")
    unavailable_ids = list(get_unavailable_seat_ids(trip))  # for template "in" checks

    if request.method == "POST":
        selected = request.POST.getlist("seats")
        if not selected:
            return render(request, "buses/seat_select.html", {
                "trip": trip,
                "seats": seats,
                "unavailable_ids": unavailable_ids,
                "error": "Please select at least one seat."
            })

        selected_ids = [int(x) for x in selected]
        expires_at = timezone.now() + timedelta(minutes=LOCK_MINUTES)

        try:
            with transaction.atomic():
                now = timezone.now()

                # Cleanup expired locks for this trip (optional but useful)
                SeatLock.objects.filter(trip=trip, expires_at__lte=now).delete()

                # Check if any selected seat is already locked by another user (not expired)
                conflicting_locks = SeatLock.objects.select_for_update().filter(
                    trip=trip,
                    seat_id__in=selected_ids,
                    expires_at__gt=now
                ).exclude(user=request.user)

                if conflicting_locks.exists():
                    messages.error(request, "Some seats were just locked by someone else. Please select again.")
                    return redirect("select_seats", trip_id=trip.id)

                # Check if any selected seat is already booked (confirmed)
                booked = BookingSeat.objects.select_for_update().filter(
                    booking__trip=trip,
                    booking__status="CONFIRMED",
                    seat_id__in=selected_ids
                )
                if booked.exists():
                    messages.error(request, "Some seats were just booked. Please select again.")
                    return redirect("select_seats", trip_id=trip.id)

                # Release user's old active locks for this trip (optional)
                SeatLock.objects.filter(trip=trip, user=request.user).delete()

                # Create locks for selected seats
                for seat_id in selected_ids:
                    SeatLock.objects.create(
                        trip=trip,
                        seat_id=seat_id,
                        user=request.user,
                        expires_at=expires_at
                    )

        except IntegrityError:
            # Unique constraint hit (trip, seat) => someone locked simultaneously
            messages.error(request, "One or more seats were locked at the same time by someone else. Try again.")
            return redirect("select_seats", trip_id=trip.id)

        return redirect("checkout", trip_id=trip.id)

    return render(request, "buses/seat_select.html", {
        "trip": trip,
        "seats": seats,
        "unavailable_ids": unavailable_ids
    })


@login_required
def checkout_view(request, trip_id):
    trip = get_object_or_404(
        Trip.objects.select_related("bus", "route", "route__source", "route__destination"),
        id=trip_id, active=True
    )

    now = timezone.now()
    locks = SeatLock.objects.filter(trip=trip, user=request.user, expires_at__gt=now).select_related("seat")
    locked_seats = [l.seat for l in locks]

    if not locked_seats:
        messages.info(request, "No seats locked. Please select seats again.")
        return redirect("select_seats", trip_id=trip.id)

    total_fare = trip.base_fare * len(locked_seats)

    # show countdown label (optional)
    earliest_expiry = min(l.expires_at for l in locks)
    remaining_seconds = int((earliest_expiry - now).total_seconds())
    lock_expires_in = f"{max(0, remaining_seconds)//60}m {max(0, remaining_seconds)%60}s"

    if request.method == "POST":
        # Passenger details are posted as: name_<seat_id>, age_<seat_id>, gender_<seat_id>
        try:
            with transaction.atomic():
                now = timezone.now()

                # Re-read locks with row locks to avoid race
                locks_qs = SeatLock.objects.select_for_update().filter(
                    trip=trip, user=request.user, expires_at__gt=now
                ).select_related("seat")

                locks_list = list(locks_qs)
                if not locks_list:
                    messages.error(request, "Your seat lock expired. Please select seats again.")
                    return redirect("select_seats", trip_id=trip.id)

                seat_ids = [l.seat_id for l in locks_list]

                # Re-check if any seat got booked (should not happen, but for safety)
                if BookingSeat.objects.select_for_update().filter(
                    booking__trip=trip,
                    booking__status="CONFIRMED",
                    seat_id__in=seat_ids
                ).exists():
                    # release locks for user
                    SeatLock.objects.filter(trip=trip, user=request.user).delete()
                    messages.error(request, "Some seats were booked before confirmation. Please try again.")
                    return redirect("select_seats", trip_id=trip.id)

                # Create booking
                booking = Booking.objects.create(
                    user=request.user,
                    trip=trip,
                    status="CONFIRMED",
                    total_fare=trip.base_fare * len(seat_ids),
                )

                # Create seats & passengers
                for lock in locks_list:
                    seat = lock.seat
                    BookingSeat.objects.create(
                        booking=booking,
                        seat=seat,
                        fare=trip.base_fare
                    )

                    name = request.POST.get(f"name_{seat.id}", "").strip()
                    age = request.POST.get(f"age_{seat.id}", "").strip()
                    gender = request.POST.get(f"gender_{seat.id}", "").strip()

                    if not name or not age or not gender:
                        raise ValueError("Missing passenger details.")

                    Passenger.objects.create(
                        booking=booking,
                        seat=seat,               
                        name=name,
                        age=int(age),
                        gender=gender
                    )

                # Clear locks after booking confirmed
                SeatLock.objects.filter(trip=trip, user=request.user).delete()

        except ValueError:
            messages.error(request, "Please fill all passenger details.")
            return redirect("checkout", trip_id=trip.id)

        messages.success(request, "Booking confirmed!")
        return redirect("booking_success", booking_id=booking.id)

    return render(request, "bookings/checkout.html", {
        "trip": trip,
        "locked_seats": locked_seats,
        "total_fare": total_fare,
        "lock_expires_in": lock_expires_in
    })


@login_required
def booking_success_view(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related("trip", "trip__route", "trip__bus"),
        id=booking_id, user=request.user
    )
    return render(request, "bookings/success.html", {"booking": booking})


@login_required
def booking_history_view(request):
    bookings = (
        Booking.objects.filter(user=request.user)
        .select_related("trip", "trip__route", "trip__bus", "trip__route__source", "trip__route__destination")
        .order_by("-created_at")
    )
    return render(request, "bookings/history.html", {"bookings": bookings})


@login_required
def cancel_booking_view(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related("trip", "trip__route"),
        id=booking_id, user=request.user
    )

    if booking.status != "CONFIRMED":
        messages.info(request, "Only confirmed bookings can be cancelled.")
        return redirect("booking_history")

    if request.method == "POST":
        reason = request.POST.get("reason", "").strip()

        with transaction.atomic():
            # lock row
            booking = Booking.objects.select_for_update().get(id=booking.id)

            if booking.status != "CONFIRMED":
                messages.info(request, "Booking already updated.")
                return redirect("booking_history")

            booking.status = "CANCELLED"
            booking.cancelled_at = timezone.now()
            booking.cancellation_reason = reason
            booking.save()

        messages.success(request, "Booking cancelled.")
        return redirect("booking_history")

    return render(request, "bookings/cancel_confirm.html", {"booking": booking})


@login_required
def ticket_pdf_view(request, booking_id):
    """
    Generates downloadable PDF ticket using WeasyPrint.
    Install: pip install weasyprint
    """
    booking = get_object_or_404(
        Booking.objects.select_related(
            "trip", "trip__route", "trip__bus",
            "trip__route__source", "trip__route__destination"
        ).prefetch_related("passengers", "seats"),
        id=booking_id,
        user=request.user
    )

    # If you only allow tickets for confirmed:
    # if booking.status != "CONFIRMED": raise Http404("Ticket not available")

    html_string = render_to_string("bookings/ticket.html", {"booking": booking})

    try:
        from weasyprint import HTML
        pdf = HTML(string=html_string).write_pdf()
    except Exception as e:
        # fallback: show HTML if PDF lib missing
        return HttpResponse(html_string)

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="ticket_{booking.pnr}.pdf"'
    return response
