from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.event_list, name='list'),
    path('create/', views.create_event, name='create'),
    path('<uuid:pk>/', views.event_detail, name='detail'),
    path('<uuid:pk>/edit/', views.edit_event, name='edit'),
    path('<uuid:pk>/delete/', views.delete_event, name='delete'),
    path('category/<slug:slug>/', views.events_by_category, name='by_category'),
]
