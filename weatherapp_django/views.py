from django.shortcuts import render, redirect

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User

from django.http import JsonResponse
# from django.http import HttpResponse

import json
import urllib.request


def home(request):
    if request.method == 'POST':
        city = request.POST['city']
        lat = 30.0333
        lon = 31.2333
        res = urllib.request.urlopen('api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid=f83d7fd156d31449f81256ec49138590').read()
        json_data = json.loads(res)
        data = {
            "country_code": str(json_data['sys']['country']),
            "coordinate": str(json_data['coord']['lon']) + ' ' + str(json_data['coord']['lat']),
            "temperature": str(json_data['main']['temp']) + 'K',
            "pressure": str(json_data['main']['pressure']) + 'Pa',
            "humidity": str(json_data['main']['humidity']),
        }
    else:
        city = ""
        data = {}
    return render(request, './home/home.html', {'city': city, 'data': data})

# User Registration and Login
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        
        # Validate unique email
        if User.objects.filter(email=email).exists():
            messages.info( request, 'Email Already Used')
            return redirect('register')
        elif User.objects.filter(username=username).exists():
            messages.info( request, 'Username Already Used')
            return redirect('register')
       
        # Create a new user
        user = User.objects.create_user(username=username, password=password, email=email)
        
        # Authenticate the user and log them in
        user = authenticate(username=username, password=password)
        login(request, user)
        
        return redirect('dashboard')
    return render(request, 'auth/register.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        # Authenticate the user
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'auth/login.html', {'error_message': 'Invalid credentials'})
    
    return render(request, 'auth/login.html')

@login_required
def dashboard(request):
    user = request.user
    return render(request, 'auth/dashboard.html', {'user': user})

# User Logout
def user_logout(request):
    logout(request)
    messages.info( request, 'Logged out succesfully')
    return redirect('/')

@permission_required('auth.view_user')
def view_users(request):
    users = User.objects.all()
    # return render(request, 'auth/users.html', {'users': users})
    data = [{ 'name': user.username, 'email': user.email } for user in users ]
    return JsonResponse(data, safe=False)