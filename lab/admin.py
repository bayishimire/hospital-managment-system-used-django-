from django.contrib import admin
from .models import LabOrder

@admin.register(LabOrder)
class LabOrderAdmin(admin.ModelAdmin):
    list_display = ('test_name', 'visit', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('test_name', 'visit__fish_id', 'visit__patient__first_name')
    ordering = ('-created_at',)
