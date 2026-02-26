from django.urls import path
from .views import (
    checkout_view, booking_success_view, booking_history_view,
    cancel_booking_view, ticket_pdf_view
)

urlpatterns = [
    path("checkout/<int:trip_id>/", checkout_view, name="checkout"),
    path("success/<int:booking_id>/", booking_success_view, name="booking_success"),
    path("my/", booking_history_view, name="booking_history"),
    path("<int:booking_id>/cancel/", cancel_booking_view, name="cancel_booking"),
    path("<int:booking_id>/ticket.pdf", ticket_pdf_view, name="ticket_pdf"),
]