from django.shortcuts import render, redirect
import requests



from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User

from django.contrib.auth import logout as auth_logout

API_BASE = "http://127.0.0.1:8000/api/"  # DRF backend

# Home page - list hotels
def home(request):
    res = requests.get(f"{API_BASE}hotels/")
    hotels = res.json() if res.status_code == 200 else []
    return render(request, 'frontend_bookings/home.html', {'hotels': hotels})

# Hotel detail & rooms
def hotel_detail(request, hotel_id):
    hotel_res = requests.get(f"{API_BASE}hotels/{hotel_id}/")
    rooms_res = requests.get(f"{API_BASE}rooms/?hotel={hotel_id}")
    reviews_res = requests.get(f"{API_BASE}reviews/?hotel={hotel_id}")
    hotel = hotel_res.json() if hotel_res.status_code == 200 else {}
    rooms = rooms_res.json() if rooms_res.status_code == 200 else []
    reviews = reviews_res.json() if reviews_res.status_code == 200 else []
    return render(request, 'frontend_bookings/hotel_detail.html', {
        'hotel': hotel, 'rooms': rooms, 'reviews': reviews
    })

from django.contrib.auth.decorators import login_required

def booking_form(request, room_id):
    message = ''
    if request.method == 'POST':
        if request.user.is_staff:
            message = "Admins cannot book rooms."
        else:
            data = {
                "room": room_id,
                "traveler": request.user.id,  # logged-in traveler
                "check_in": request.POST.get('check_in'),
                "check_out": request.POST.get('check_out')
            }
            res = requests.post(f"{API_BASE}bookings/", json=data)
            message = "Booking successful!" if res.status_code in [200, 201] else "Booking failed."

    room_res = requests.get(f"{API_BASE}rooms/{room_id}/")
    room = room_res.json() if room_res.status_code == 200 else {}

    return render(request, 'frontend_bookings/booking_form.html', {'room': room, 'message': message})


def signup(request):
    message = ''
    if request.method == 'POST':
        data = {
            "username": request.POST.get('username'),
            "email": request.POST.get('email'),
            "password": request.POST.get('password'),
        }
        res = requests.post(f"{API_BASE}users/", json=data)
        if res.status_code in [200, 201]:
            return redirect('login')
        else:
            message = "Signup failed. Try a different username/email."
    return render(request, 'frontend_bookings/signup.html', {'message': message})

from django.contrib.auth import authenticate, login as auth_login

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login

def login(request):
    message = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate against DRF User model
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)  # login sets request.user
            return redirect('home')    # redirect to homepage
        else:
            message = "Invalid credentials."

    return render(request, 'frontend_bookings/login.html', {'message': message})

def reviews(request, hotel_id):
    hotel_res = requests.get(f"{API_BASE}hotels/{hotel_id}/")
    reviews_res = requests.get(f"{API_BASE}reviews/?hotel={hotel_id}")

    hotel = hotel_res.json() if hotel_res.status_code == 200 else {}
    reviews = reviews_res.json() if reviews_res.status_code == 200 else []

    return render(request, 'frontend/reviews.html', {
        'hotel': hotel,
        'reviews': reviews
    })



def logout(request):
    auth_logout(request)
    return redirect('home')
