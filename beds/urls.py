from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='bed_dashboard'),
    path('manage/', views.manage_beds, name='manage_beds'),
    path('ward/<int:pk>/edit/', views.edit_ward, name='edit_ward'),
    path('bed/<int:pk>/edit/', views.edit_bed, name='edit_bed'),
]
