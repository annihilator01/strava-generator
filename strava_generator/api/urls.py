from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('v1/', include('strava_generator.api.v1.urls')),
]
