from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('hotel/<int:hotel_id>/', views.hotel_detail, name='hotel_detail'),
    path('hotel/<int:hotel_id>/reviews/', views.reviews, name='reviews'),
    path('book/<int:room_id>/', views.booking_form, name='booking_form'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),

]


from django.conf import settings
from django.conf.urls.static import static


# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
