from django.db import models
from reception.models import PatientVisit

class LabOrder(models.Model):
    LAB_STATUS = [
        ('Pending', 'Pending'),
        ('Sample Collected', 'Sample Collected'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    visit = models.ForeignKey(PatientVisit, on_delete=models.CASCADE, related_name='lab_orders')
    test_name = models.CharField(max_length=200)
    instructions = models.TextField(blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=LAB_STATUS, default='Pending')
    results = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.test_name} order for {self.visit.fish_id}"
