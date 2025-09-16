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
    token = request.session.get("token")  # get token from session

    if request.method == 'POST':
        if not token:
            message = "You must be logged in as traveler to book."
        else:
            data = {
                "room": room_id,
                "check_in": request.POST.get('check_in'),
                "check_out": request.POST.get('check_out')
            }
            headers = {"Authorization": f"Token {token}"}
            res = requests.post(f"{API_BASE}bookings/", json=data, headers=headers)
            print("Booking API Response:", res.status_code, res.text)

            if res.status_code in [200, 201]:
                message = "Booking successful!"
            else:
                message = f"Booking failed: {res.text}"

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
        }
        res = requests.post(f"{API_BASE}users/", json=data)
        if res.status_code in [200, 201]:
            return redirect('login')
        else:
            message = "Signup failed. Try a different username/email."
    return render(request, 'frontend_bookings/signup.html', {'message': message})


# Login
def login(request):
    message = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        res = requests.post(f"{API_BASE}login/", json={
            "username": username,
            "password": password
        })

        response_data = res.json()
        if res.status_code == 200 and 'token' in response_data:
            # Save session info
            request.session['user_id'] = response_data.get('id')
            request.session['username'] = response_data.get('username')
            request.session['role'] = response_data.get('role')
            request.session['token'] = response_data.get('token')
            return redirect('home')
        else:
            # Show error from DRF or generic
            message = response_data.get('error', "Invalid credentials.")

    return render(request, 'frontend_bookings/login.html', {'message': message})


# Logout
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
