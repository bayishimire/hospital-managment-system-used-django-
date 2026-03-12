from django.db import models
from django.utils import timezone
import random
import string

class Patient(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    patient_id = models.CharField(max_length=20, unique=True, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    
    # Contact Info
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField()
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=200)
    emergency_contact_phone = models.CharField(max_length=20)
    
    # Insurance
    INSURANCE_CHOICES = [
        ('None', 'No Insurance / Cash Pay'),
        ('RSSB-Mutuelle', 'RSSB / Mutuelle (Rwanda)'),
        ('RSSB-RAMA', 'RSSB / RAMA (Rwanda)'),
        ('MMI', 'MMI (Rwanda)'),
        ('Radiant', 'Radiant (Rwanda)'),
        ('Sanlam', 'Sanlam (Rwanda)'),
        ('UAP', 'UAP (Rwanda)'),
        ('Aetna', 'Aetna (International)'),
        ('Cigna', 'Cigna (International)'),
        ('Bupa', 'Bupa (International)'),
        ('Other', 'Other')
    ]
    insurance_provider = models.CharField(max_length=100, choices=INSURANCE_CHOICES, default='None')
    insurance_policy_number = models.CharField(max_length=100, blank=True, null=True)
    is_insurance_verified = models.BooleanField(default=False)
    verification_notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.patient_id:
            # Generate unique Patient ID: P-YYYYMM-XXXX
            prefix = "P-" + timezone.now().strftime("%Y%m")
            while True:
                suffix = ''.join(random.choices(string.digits, k=4))
                new_id = f"{prefix}-{suffix}"
                if not Patient.objects.filter(patient_id=new_id).exists():
                    self.patient_id = new_id
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.patient_id})"
