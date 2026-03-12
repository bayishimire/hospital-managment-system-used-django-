from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'employee_id', 'department', 'is_active')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'employee_id')
    ordering = ('-created_at',)

    fieldsets = UserAdmin.fieldsets + (
        ('HMS Profile', {
            'fields': ('role', 'phone', 'address', 'employee_id', 'department'),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('HMS Profile', {
            'fields': ('first_name', 'last_name', 'email', 'role', 'phone', 'employee_id', 'department'),
        }),
    )
