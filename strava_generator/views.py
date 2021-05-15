from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from django.db import DatabaseError
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from strava_generator.api.v1.views import get_generated_strava_gpx
from . import service


@login_required(login_url='/signin')
@service.user_active_status_required
@service.active_usage_token_required
def index(request):
    return render(request, 'strava_generator/index.html')


@service.handle_signin_info
def signin(request):
    service.register_visit(request)

    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            return render(request, 'strava_generator/registration/signin.html', {'error_info': 'Incorrect username or password'})
    else:
        return render(request, 'strava_generator/registration/signin.html')


def signup(request):
    service.register_visit(request)

    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password-confirm')
        usage_token = request.POST.get('usage-token')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            return render(request, 'strava_generator/registration/signup.html',
                          {'error_info': f'User with username \'{username}\' already exists'})
        else:
            try:
                service.validate_username(username)
                service.validate_password(password)
                service.validate_password_confirm(password_confirm, password)
                service.validate_usage_token(usage_token)
            except ValidationError as ve:
                return render(request, 'strava_generator/registration/signup.html',
                       {'error_info': ve.args[0]})

            try:
                user = service.register_user(
                    username=username,
                    password=password,
                    usage_token=usage_token
                )
            except DatabaseError:
                return render(request, 'strava_generator/registration/signup.html',
                       {'error_info': 'User is not created. Try again'})

            login(request, user)
            return redirect('/')
    else:
        return render(request, 'strava_generator/registration/signup.html')


def signout(request):
    logout(request)
    request.session['check'] = True
    return redirect('/signin')


@login_required(login_url='/signin')
@service.user_active_status_required
def update_usage_token(request):
    if request.method == 'POST':
        user = request.user
        usage_token = request.POST.get('usage-token')

        try:
            service.validate_usage_token(usage_token)
        except ValidationError as ve:
            return render(request, 'strava_generator/registration/update_usage_token.html',
                          {'error_info': ve.args[0]})

        try:
            service.update_usage_token(
                user=user,
                new_active_usage_token=usage_token,
            )
        except DatabaseError:
            return render(request, 'strava_generator/registration/update_usage_token.html',
                          {'error_info': 'Token is not updated. Try again'})

        return redirect('/')
    else:
        return render(request, 'strava_generator/registration/update_usage_token.html')
