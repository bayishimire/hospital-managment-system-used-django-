from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='reception_dashboard'),
    path('visit/<int:pk>/edit/', views.edit_visit, name='edit_visit'),
    path('visit/<int:pk>/delete/', views.delete_visit, name='delete_visit'),
]
