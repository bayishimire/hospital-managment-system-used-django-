from django.contrib import admin
from .models import PatientVisit

@admin.register(PatientVisit)
class PatientVisitAdmin(admin.ModelAdmin):
    list_display = ('fish_id', 'patient', 'assigned_doctor', 'department', 'priority', 'status', 'created_at')
    search_fields = ('fish_id', 'patient__first_name', 'patient__last_name', 'patient__patient_id')
    list_filter = ('status', 'priority', 'department', 'created_at')
    ordering = ('-created_at',)
