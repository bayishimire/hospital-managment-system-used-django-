from django.contrib import admin
from .models import Ward, Bed

@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    list_display = ('name', 'ward_type', 'capacity', 'manager')
    list_filter = ('ward_type',)
    search_fields = ('name',)

@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):
    list_display = ('bed_number', 'ward', 'is_occupied', 'current_patient')
    list_filter = ('is_occupied', 'ward')
    search_fields = ('bed_number', 'ward__name')
