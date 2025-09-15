from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('hotel/<int:hotel_id>/', views.hotel_detail, name='hotel_detail'),
    path('hotel/<int:hotel_id>/reviews/', views.reviews, name='reviews'),
    path('book/<int:room_id>/', views.booking_form, name='booking_form'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
]
