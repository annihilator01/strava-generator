from django.shortcuts import render
from . import service


def index(request):
    service.register_visit(request)
    return render(request, 'strava_generator/index.html')
