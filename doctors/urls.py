from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='doctor_dashboard'),
    path('treatment/<str:fish_id>/', views.start_treatment, name='start_treatment'),
    path('notification/read/<int:notif_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('patient-search/', views.patient_search, name='patient_search'),
    path('my-appointments/', views.my_appointments, name='my_appointments'),
    path('medical-library/', views.medical_library, name='medical_library'),
]
