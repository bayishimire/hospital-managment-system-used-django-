from django.db import models
from django.conf import settings
from django.utils import timezone
from patients.models import Patient
import random
import string

class PatientVisit(models.Model):
    STATUS_CHOICES = [
        ('Waiting', 'Waiting for Doctor'),
        ('Consulting', 'In Consultation'),
        ('Lab', 'In Laboratory'),
        ('Pharmacy', 'In Pharmacy'),
        ('Admitted', 'Admitted'),
        ('Billing', 'Waiting for Payment'),
        ('Discharged', 'Discharged'),
    ]
    
    PRIORITY_CHOICES = [
        ('Normal', 'Normal'),
        ('Urgent', 'Urgent'),
        ('Emergency', 'Emergency'),
    ]

    DEPARTMENT_CHOICES = [
        ('General OPD', 'General OPD'),
        ('Cardiology', 'Cardiology'),
        ('Neurology', 'Neurology'),
        ('Pediatrics', 'Pediatrics'),
        ('Maternity', 'Maternity'),
        ('Orthopedics', 'Orthopedics'),
        ('Internal Medicine', 'Internal Medicine'),
        ('Surgery', 'Surgery'),
        ('Dental', 'Dental'),
        ('Eye Clinic', 'Eye Clinic'),
        ('ENT', 'ENT (Ear, Nose, Throat)'),
        ('Oncology', 'Oncology'),
        ('Emergency', 'Emergency Room (ER)'),
    ]

    fish_id = models.CharField(max_length=20, unique=True, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='visits')
    
    # Doctor Assignment
    assigned_doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_patients',
        limit_choices_to={'role': 'Doctor'}
    )
    
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES, default='General OPD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Waiting')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Normal')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.fish_id:
            # Generate unique Fish ID: F-YYYYMM-XXXX
            prefix = "F-" + timezone.now().strftime("%Y%m")
            while True:
                suffix = ''.join(random.choices(string.digits, k=4))
                new_id = f"{prefix}-{suffix}"
                if not PatientVisit.objects.filter(fish_id=new_id).exists():
                    self.fish_id = new_id
                    break
        super().save(*args, **kwargs)

    @property
    def status_color(self):
        colors = {
            'Waiting': 'secondary',
            'Consulting': 'primary',
            'Lab': 'info',
            'Pharmacy': 'warning',
            'Admitted': 'danger',
            'Billing': 'dark',
            'Discharged': 'success',
        }
        return colors.get(self.status, 'secondary')

    def __str__(self):
        return f"Fish {self.fish_id} - {self.patient.first_name} ({self.status})"
