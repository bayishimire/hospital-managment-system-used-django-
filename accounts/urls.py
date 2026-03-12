from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('redirect/', views.redirect_dashboard, name='redirect_dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('admin-panel/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('staff-management/', views.staff_management, name='staff_management'),
    path('register/', views.register_view, name='register'),
    path('monitor/clinical/', views.clinical_monitor, name='clinical_monitor'),
    path('monitor/lab/', views.lab_monitor, name='lab_monitor'),
    path('monitor/pharmacy/', views.pharmacy_monitor, name='pharmacy_monitor'),
    path('monitor/finance/', views.finance_monitor, name='finance_monitor'),
    path('staff/<int:pk>/edit/', views.edit_staff, name='edit_staff'),
    path('staff/<int:pk>/delete/', views.delete_staff, name='delete_staff'),
]
