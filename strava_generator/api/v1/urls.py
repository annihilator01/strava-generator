from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('generate-strava-gpx', views.get_generated_strava_gpx, name='api-v1-generate-strava-gpx'),
]
