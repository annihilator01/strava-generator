from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from . import service


@login_required(login_url='/signin')
def index(request):
    service.register_visit(request)
    return render(request, 'strava_generator/index.html')


def signin(request):
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
    return render(request, 'strava_generator/registration/signup.html')


def signout(request):
    logout(request)
    return redirect('/signin')