from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('book/<uuid:event_pk>/', views.book_event, name='book'),
    path('confirmation/<uuid:booking_id>/', views.booking_confirmation, name='confirmation'),
    path('cancel/<uuid:booking_id>/', views.cancel_booking, name='cancel'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
]
