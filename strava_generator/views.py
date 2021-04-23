from django.shortcuts import render
from . import service


def index(request):
    service.register_visitor(request)
    return render(request, 'strava_generator/index.html')
