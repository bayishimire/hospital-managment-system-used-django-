from django.db import models
from django.conf import settings

class Ward(models.Model):
    name = models.CharField(max_length=100)
    ward_type = models.CharField(max_length=50, choices=[
        ('General', 'General'),
        ('ICU', 'ICU'),
        ('Pediatric', 'Pediatric'),
        ('Maternity', 'Maternity'),
        ('Surgical', 'Surgical'),
    ])
    capacity = models.PositiveIntegerField()
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_wards',
        limit_choices_to={'role': 'WardManager'}
    )

    def __str__(self):
        return f"{self.name} ({self.ward_type})"

class Bed(models.Model):
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE, related_name='beds')
    bed_number = models.CharField(max_length=20)
    is_occupied = models.BooleanField(default=False)
    current_patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_bed'
    )

    def __str__(self):
        return f"Bed {self.bed_number} - {self.ward.name}"
