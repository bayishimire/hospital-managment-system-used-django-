from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='lab_dashboard'),
    path('complete/<str:fish_id>/', views.complete_lab, name='complete_lab'),
    path('order/<int:pk>/edit/', views.edit_lab_order, name='edit_lab_order'),
]
