
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('Doctor', 'Doctor'),
        ('Reception', 'Reception'),
        ('Lab', 'Laboratory Staff'),
        ('Pharmacy', 'Pharmacist'),
        ('Payments', 'Billing Staff'),
        ('Nurse', 'Nurse'),
        ('WardManager', 'Ward Manager'),
        ('Admin', 'Administrator'),
    ]

    # Required fields
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name="Select Role")
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    # Status & Management
    is_on_duty = models.BooleanField(default=True)
    schedule = models.CharField(max_length=100, blank=True, null=True) # e.g. Mon-Fri 08:00-16:00
    
    # Tracking fields
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Optional additional fields for hospital context
    employee_id = models.CharField(max_length=20, blank=True, null=True)  # Staff ID
    department = models.CharField(max_length=50, blank=True, null=True)   # e.g., Cardiology, Pharmacy
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role}) - {self.created_at} {self.updated_at}"