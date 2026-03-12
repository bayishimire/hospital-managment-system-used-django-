from django.contrib import admin
from .models import StaffNotification

@admin.register(StaffNotification)
class StaffNotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'title', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at', 'recipient')
    search_fields = ('title', 'message', 'recipient__username')
    ordering = ('-created_at',)
