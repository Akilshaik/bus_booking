from django.contrib import admin
from django.urls import path
from django.utils.html import format_html
from django.http import HttpResponse
from .models import Booking, Passenger, SeatLock, BookingSeat
from . import admin_pdf_views, reports_pdf_views


# Register other models
admin.site.register(BookingSeat)
admin.site.register(SeatLock)
admin.site.register(Passenger)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("trip", "user", "total_fare", "created_at", "download_pdf")
    change_list_template = "admin/bookings/change_list_with_report.html"  # ✅ custom template

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            # ticket PDF for single booking
            path(
                "<int:booking_id>/pdf/",
                self.admin_site.admin_view(admin_pdf_views.booking_pdf),
                name="booking_pdf",
            ),
            # reports
            path(
                "reports/",
                self.admin_site.admin_view(self.reports_dashboard),
                name="reports_dashboard",
            ),
            path(
                "reports/all-bookings/",
                self.admin_site.admin_view(reports_pdf_views.all_bookings_report),
            ),
            path(
                "reports/all-passengers/",
                self.admin_site.admin_view(reports_pdf_views.all_passengers_report),
            ),
            path(
                "reports/todays-routes/",
                self.admin_site.admin_view(reports_pdf_views.todays_routes_report),
            ),
        ]
        return custom_urls + urls

    def reports_dashboard(self, request):
        """Custom reports dashboard with buttons."""
        html = """
        <h1>📊 Generate Reports</h1>
        <p>Select which report you want to download:</p>
        <div style="display:flex; gap:15px; margin-top:20px;">
            <a class="button" href="all-bookings/">📄 All Bookings</a>
            <a class="button" href="all-passengers/">👥 All Passengers</a>
            <a class="button" href="todays-routes/">🚌 Today's Routes</a>
        </div>
        <style>
            .button {
                background-color: #0C4B33;
                color: white;
                padding: 10px 15px;
                border-radius: 5px;
                text-decoration: none;
                font-weight: bold;
            }
            .button:hover { background-color: #18664f; }
        </style>
        """
        return HttpResponse(html)

    def download_pdf(self, obj):
        return format_html('<a class="button" href="{}/pdf/">Download PDF</a>', obj.id)

    download_pdf.short_description = "Download Ticket"