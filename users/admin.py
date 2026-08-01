from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'is_approved', 'is_active', 'date_joined']
    list_filter = ['role', 'is_approved', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Marketplace role', {'fields': ('role', 'is_approved', 'phone')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Marketplace role', {'fields': ('role', 'is_approved', 'phone', 'email')}),
    )
