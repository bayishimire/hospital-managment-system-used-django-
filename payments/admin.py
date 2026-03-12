from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('visit', 'amount', 'method', 'status', 'collected_by', 'created_at')
    list_filter = ('status', 'method', 'created_at')
    search_fields = ('visit__fish_id', 'visit__patient__first_name', 'visit__patient__last_name')
    ordering = ('-created_at',)
