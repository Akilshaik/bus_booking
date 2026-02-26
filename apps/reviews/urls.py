from django.urls import path
from .views import add_review_view, bus_reviews_view

urlpatterns = [
    path("bus/<int:bus_id>/", bus_reviews_view, name="bus_reviews"),
    path("bus/<int:bus_id>/add/", add_review_view, name="add_review"),
]