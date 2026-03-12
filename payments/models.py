from django.db import models
from django.conf import settings
from reception.models import PatientVisit

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('Cash', 'Cash'),
        ('Insurance', 'Insurance'),
        ('MobileMoney', 'Mobile Money'),
        ('Card', 'Credit/Debit Card'),
    ]
    
    visit = models.ForeignKey(PatientVisit, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Partial', 'Partial Payment'),
        ('Refunded', 'Refunded'),
    ], default='Pending')
    
    collected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='collected_payments',
        limit_choices_to={'role': 'Payments'}
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment for {self.visit.fish_id} - {self.amount} ({self.status})"
