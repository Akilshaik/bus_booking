from django.urls import path
from .views import bus_select, bus_reviews_view, add_review_view

urlpatterns = [
    path("buses/", bus_select, name="bus_select"),
    path("buses/<int:bus_id>/reviews/", bus_reviews_view, name="bus_reviews"),
    path("buses/<int:bus_id>/review/add/", add_review_view, name="add_review"),
]