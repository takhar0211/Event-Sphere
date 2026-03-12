from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_verified', 'date_joined']
    list_filter = ['role', 'is_verified', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Profile', {'fields': ('role', 'phone', 'bio', 'avatar', 'organization', 'is_verified')}),
    )
