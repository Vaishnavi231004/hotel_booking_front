from django.shortcuts import render, redirect
import requests
from .forms import ReviewForm
from django.contrib import messages

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


from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def booking_form(request, room_id):
    message = ''
    token = request.session.get("token")  # DRF token in session

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

    return render(request, 'frontend_bookings/booking_form.html', {
        'room': room, 'message': message
    })


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



def add_review(request, hotel_id):
    token = request.session.get("token")
    if not token:
        messages.error(request, "You must be logged in to add a review.")
        return redirect("login")

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            data = {
                "hotel": hotel_id,
                "traveler": request.session.get("user_id"),
                "rating": form.cleaned_data["rating"],
                "comment": form.cleaned_data["comment"],
            }
            headers = {"Authorization": f"Token {token}"}
            res = requests.post(f"{API_BASE}reviews/", json=data, headers=headers)

            if res.status_code == 201:
                messages.success(request, "Review added successfully!")
                return redirect("hotel_detail", hotel_id=hotel_id)
            else:
                messages.error(request, f"Failed to add review: {res.text}")
    else:
        form = ReviewForm()

    return render(request, "frontend_bookings/review_form.html", {"form": form, "action": "Add"})


# Edit Review
def edit_review(request, review_id):
    token = request.session.get("token")
    headers = {"Authorization": f"Token {token}"} if token else {}

    # Fetch review
    res = requests.get(f"{API_BASE}reviews/{review_id}/", headers=headers)
    if res.status_code != 200:
        messages.error(request, "Review not found.")
        return redirect("home")

    review = res.json()

    # Check ownership (traveler is username in DRF response)
    if review["traveler"] != request.session.get("username"):
        messages.error(request, "You can only edit your own reviews.")
        return redirect("hotel_detail", hotel_id=review["hotel"])

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            data = {
                "hotel": review["hotel"],  # hotel ID
                "traveler": request.session.get("user_id"),  # user ID for DRF
                "rating": form.cleaned_data["rating"],
                "comment": form.cleaned_data["comment"],
            }
            update_res = requests.put(f"{API_BASE}reviews/{review_id}/", json=data, headers=headers)
            if update_res.status_code in [200, 201]:
                messages.success(request, "Review updated successfully!")
                return redirect("hotel_detail", hotel_id=review["hotel"])
            else:
                messages.error(request, f"Failed to update review: {update_res.text}")
    else:
        # Pre-fill form
        form = ReviewForm(initial={"rating": review["rating"], "comment": review["comment"]})

    return render(request, "frontend_bookings/review_form.html", {"form": form, "action": "Edit", "hotel_id": review["hotel"]})


# Delete Review
def delete_review(request, review_id):
    token = request.session.get("token")
    headers = {"Authorization": f"Token {token}"} if token else {}

   
    res = requests.get(f"{API_BASE}reviews/{review_id}/", headers=headers)
    if res.status_code != 200:
        messages.error(request, "Review not found.")
        return redirect("home")

    review = res.json()

    
    if review["traveler"] != request.session.get("username"):
        messages.error(request, "You can only delete your own reviews.")
        return redirect("hotel_detail", hotel_id=review["hotel"])

   
    delete_res = requests.delete(f"{API_BASE}reviews/{review_id}/", headers=headers)
    if delete_res.status_code == 204:
        messages.success(request, "Review deleted successfully!")
    else:
        messages.error(request, f"Failed to delete review: {delete_res.text}")

    return redirect("hotel_detail", hotel_id=review["hotel"])
