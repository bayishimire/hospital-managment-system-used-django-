from django.contrib import admin
from .models import Consultation

@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('visit', 'diagnosis', 'created_at')
    search_fields = ('visit__fish_id', 'visit__patient__first_name', 'diagnosis')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
