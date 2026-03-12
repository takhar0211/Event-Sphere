from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['short_id', 'user', 'event', 'quantity', 'total_price', 'status', 'booked_at']
    list_filter = ['status', 'booked_at']
    search_fields = ['user__username', 'event__title']
    readonly_fields = ['booking_id', 'booked_at']
