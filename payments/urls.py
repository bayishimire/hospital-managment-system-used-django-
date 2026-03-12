from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='payments_dashboard'),
    path('payment/<int:pk>/edit/', views.edit_payment, name='edit_payment'),
    path('process/<str:fish_id>/', views.process_payment, name='process_payment'),
    path('insurance/<str:fish_id>/', views.insurance_claim, name='insurance_claim'),
    path('receipt/<str:fish_id>/', views.print_receipt, name='print_receipt'),
    path('report/', views.view_report, name='view_report'),
]
