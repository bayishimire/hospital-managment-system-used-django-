from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='pharmacy_dashboard'),
    path('dispense/<str:fish_id>/', views.dispense_medication, name='dispense_medication'),
    path('medication/<int:pk>/edit/', views.edit_medication, name='edit_medication'),
]
