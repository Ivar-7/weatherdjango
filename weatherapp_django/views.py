from django.shortcuts import render, redirect

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User

from django.http import JsonResponse
from django.http import HttpResponse

import json
import urllib.request
import requests
import datetime
import base64
from requests.auth import HTTPBasicAuth


def home(request):
    if request.method == 'POST':
        city = request.POST['city']
        lat = 30.0333
        lon = 31.2333
        res = urllib.request.urlopen('api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid=').read()
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

# Mpesa
def mpesa_payment(request):
    if request.method == 'POST':
        phone = str(request.POST.get('phone'))
        amount = str(request.POST.get('amount'))

        # GENERATING THE ACCESS TOKEN
        consumer_key = "GTWADFxIpUfDoNikNGqq1C3023evM6UH"
        consumer_secret = "amFbAoUByPV2rM5A"
        api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

        r = requests.get(api_url, auth=HTTPBasicAuth(consumer_key, consumer_secret))
        data = r.json()
        access_token = "Bearer" + ' ' + data['access_token']

        # GETTING THE PASSWORD
        timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
        passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
        business_short_code = "174379"
        data = business_short_code + passkey + timestamp
        encoded = base64.b64encode(data.encode())
        password = encoded.decode('utf-8')

        # BODY OR PAYLOAD
        payload = {
            "BusinessShortCode": "174379",
            "Password": "{}".format(password),
            "Timestamp": "{}".format(timestamp),
            "TransactionType": "CustomerPayBillOnline",
            "Amount": "1",  # use 1 when testing
            "PartyA": phone,  # change to your number
            "PartyB": "174379",
            "PhoneNumber": phone,
            "CallBackURL": "https://modcom.co.ke/job/confirmation.php",
            "AccountReference": "account",
            "TransactionDesc": "account"
        }

        # POPULATING THE HTTP HEADER
        headers = {
            "Authorization": access_token,
            "Content-Type": "application/json"
        }

        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"  # C2B URL

        response = requests.post(url, json=payload, headers=headers)
        print(response.text)

        return HttpResponse('<h3>Please Complete Payment in Your Phone and we will deliver in minutes</h3>'
                            '<a href="/" class="btn btn-dark btn-sm">Back to Products</a>')

    return render(request, './home/mpesa.html')
