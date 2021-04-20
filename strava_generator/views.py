from django.shortcuts import render


def index(request):
    return render(request, 'strava_generator/index.html')
