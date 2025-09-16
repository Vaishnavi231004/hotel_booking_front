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


# Booking form - traveler must be logged in
def booking_form(request, room_id):
    message = ''
    user_id = request.session.get("user_id")
    if request.method == 'POST':
        if not user_id:
            message = "You must be logged in as traveler to book."
        else:
            data = {
                "room": room_id,
                "traveler": user_id,
                "check_in": request.POST.get('check_in'),
                "check_out": request.POST.get('check_out')
            }
            res = requests.post(f"{API_BASE}bookings/", json=data)
            message = "Booking successful!" if res.status_code in [200, 201] else "Booking failed."

    room_res = requests.get(f"{API_BASE}rooms/{room_id}/")
    room = room_res.json() if room_res.status_code == 200 else {}

    return render(request, 'frontend_bookings/booking_form.html', {'room': room, 'message': message})


# Traveler signup
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



def login(request):
    message = ''
    if request.method == 'POST':
        data = {
            "username": request.POST.get('username'),
            "password": request.POST.get('password')
        }
        res = requests.post(f"{API_BASE}login/", json=data)  # <-- DRF login endpoint
        if res.status_code == 200:
            user = res.json()
            # store session info
            request.session['user_id'] = user['id']
            request.session['username'] = user['username']
            request.session['role'] = user['role']
            return redirect('home')
        else:
            message = "Invalid credentials."

    return render(request, 'frontend_bookings/login.html', {'message': message})


def logout(request):
    request.session.flush()  
    return redirect('home')


# Reviews
def reviews(request, hotel_id):
    hotel_res = requests.get(f"{API_BASE}hotels/{hotel_id}/")
    reviews_res = requests.get(f"{API_BASE}reviews/?hotel={hotel_id}")

    hotel = hotel_res.json() if hotel_res.status_code == 200 else {}
    reviews = reviews_res.json() if reviews_res.status_code == 200 else []

    return render(request, 'frontend_bookings/reviews.html', {
        'hotel': hotel,
        'reviews': reviews
    })
