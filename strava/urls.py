from django.contrib import admin
from django.urls import path, include

# html-based urls
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('strava_generator.urls')),
]

# api-based urls
urlpatterns += [
    path('api/', include('strava_generator.api.urls')),
]
