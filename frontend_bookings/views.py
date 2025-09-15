from django.shortcuts import render, redirect
import requests

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

# Booking form
def booking_form(request, room_id):
    message = ''
    if request.method == 'POST':
        data = {
            "room": room_id,
            "traveler": 1,  # replace with session user id later
            "check_in": request.POST.get('check_in'),
            "check_out": request.POST.get('check_out')
        }
        res = requests.post(f"{API_BASE}bookings/", data=data)
        message = "Booking successful!" if res.status_code in [200,201] else "Booking failed."
    room_res = requests.get(f"{API_BASE}rooms/{room_id}/")
    room = room_res.json() if room_res.status_code == 200 else {}
    return render(request, 'frontend_bookings/booking_form.html', {'room': room, 'message': message})

# Signup
def signup(request):
    message = ''
    if request.method == 'POST':
        data = {
            "username": request.POST.get('username'),
            "email": request.POST.get('email'),
            "password": request.POST.get('password'),
            "role": "traveler"
        }
        res = requests.post(f"{API_BASE}users/", data=data)
        message = "Signup successful!" if res.status_code in [200,201] else "Signup failed."
    return render(request, 'frontend_bookings/signup.html', {'message': message})

# Login (basic, without session)
def login(request):
    message = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        res = requests.get(f"{API_BASE}users/?username={username}")
        users = res.json() if res.status_code == 200 else []
        if users and users[0]['password'] == password:
            message = "Login successful!"
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
