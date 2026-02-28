from django.shortcuts import render

# Create your views here.

# apps/core/views.py
from django.http import HttpResponse

def health(request):
    return HttpResponse("ok", content_type="text/plain")