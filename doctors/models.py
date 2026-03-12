from django.db import models
from reception.models import PatientVisit

class Consultation(models.Model):
    visit = models.OneToOneField(PatientVisit, on_delete=models.CASCADE, related_name='consultation')
    
    # Clinical Notes
    symptoms = models.TextField()
    diagnosis = models.TextField()
    treatment_plan = models.TextField()
    
    # Vital Signs (Optional but good for medical records)
    blood_pressure = models.CharField(max_length=20, blank=True, null=True)
    temperature = models.CharField(max_length=10, blank=True, null=True)
    heart_rate = models.CharField(max_length=10, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Consultation for {self.visit.fish_id}"
