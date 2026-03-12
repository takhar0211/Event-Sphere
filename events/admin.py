from django.contrib import admin
from .models import Event, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'organizer', 'category', 'date', 'status', 'available_tickets', 'ticket_price']
    list_filter = ['status', 'category', 'date']
    search_fields = ['title', 'organizer__username', 'location']
    readonly_fields = ['id', 'created_at', 'updated_at']
