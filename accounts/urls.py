from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('register/organizer/', views.register_organizer, name='register_organizer'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
]
