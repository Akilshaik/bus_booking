from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from django.shortcuts import get_object_or_404
from .models import Booking

def booking_pdf(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    template = get_template("admin/booking_pdf.html")
    html = template.render({"booking": booking})
    
    result = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result)
    
    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)
    
    response = HttpResponse(result.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="booking_{booking_id}.pdf"'
    return response