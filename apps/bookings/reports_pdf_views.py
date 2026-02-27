from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from datetime import date
from .models import Booking, Passenger
from apps.core.models import Route

from django.utils import timezone

def generate_pdf(template_path, context, filename):
    template = get_template(template_path)
    html = template.render(context)
    result = BytesIO()
    pdf = pisa.CreatePDF(html, dest=result)
    if pdf.err:
        return HttpResponse("Error generating PDF", status=500)
    response = HttpResponse(result.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename={filename}.pdf'
    return response

def all_bookings_report(request):
    bookings = Booking.objects.select_related("trip", "user").all()
    return generate_pdf("admin/reports/all_bookings.html", {"bookings": bookings}, "all_bookings")

def all_passengers_report(request):
    today = timezone.localdate()

    passengers = Passenger.objects.filter(
        booking__status="CONFIRMED",
        booking__trip__journey_date=today
    ).select_related("booking", "booking__trip", "seat")

    return generate_pdf(
        "admin/reports/all_passengers.html",
        {"passengers": passengers},
        "today_passengers"
    )

def todays_routes_report(request):
    today = date.today()
    routes = Route.objects.all()  # adjust if your trip model differs
    return generate_pdf("admin/reports/todays_routes.html", {"routes": routes, "today": today}, "todays_routes")