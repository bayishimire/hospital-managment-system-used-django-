from django.contrib import admin
from .models import Medication, Prescription

@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'stock_quantity', 'low_stock_threshold', 'unit_price')
    list_filter = ('category',)
    search_fields = ('name',)

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('visit', 'medication_name', 'is_dispensed', 'created_at')
    list_filter = ('is_dispensed', 'created_at')
    search_fields = ('visit__fish_id', 'visit__patient__first_name', 'medication_name')
