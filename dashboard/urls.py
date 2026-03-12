from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.user_dashboard, name='user_dashboard'),
    path('organizer/', views.organizer_dashboard, name='organizer_dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/events/', views.admin_events, name='admin_events'),
    path('admin/bookings/', views.admin_bookings, name='admin_bookings'),
    path('admin/users/<int:user_id>/toggle/', views.toggle_user_status, name='toggle_user'),
]
