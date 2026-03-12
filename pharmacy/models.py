from django.db import models
from reception.models import PatientVisit

class Medication(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100, choices=[
        ('Antibiotics', 'Antibiotics'),
        ('Painkillers', 'Painkillers'),
        ('Vaccines', 'Vaccines'),
        ('Antiviral', 'Antiviral'),
        ('Other', 'Other'),
    ])
    stock_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=10)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return self.name

class Prescription(models.Model):
    visit = models.ForeignKey(PatientVisit, on_delete=models.CASCADE, related_name='prescriptions')
    
    medication_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    instructions = models.TextField(blank=True, null=True)
    
    is_dispensed = models.BooleanField(default=False)
    dispensed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.medication_name} for {self.visit.fish_id}"
