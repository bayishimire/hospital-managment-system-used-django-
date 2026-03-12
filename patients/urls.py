from django.urls import path
from . import views

urlpatterns = [
    path('directory/', views.patient_list, name='patient_list'),
    path('<int:pk>/edit/', views.patient_edit, name='patient_edit'),
]
