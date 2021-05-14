from django.contrib import admin
from django.urls import path, include

from . import views
from rest_framework.authtoken import views as rest_framework_views


urlpatterns = [
    path('', views.index, name='strava-gen'),
    path('signin/', views.signin, name='sign-in'),
    path('signup/', views.signup, name='sign-up'),
    path('update-usage-token/', views.update_usage_token, name='update-usage-token'),
    path('signout/', views.signout, name='sign-out'),
    path('get_auth_token/', rest_framework_views.obtain_auth_token, name='get_auth_token'),
]
