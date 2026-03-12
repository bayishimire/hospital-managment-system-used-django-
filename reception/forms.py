from django import forms
from .models import PatientVisit
from django.contrib.auth import get_user_model

User = get_user_model()

class PatientVisitForm(forms.ModelForm):
    class Meta:
        model = PatientVisit
        fields = ['patient', 'assigned_doctor', 'department', 'priority']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'assigned_doctor': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show doctors in the doctor assignment field
        self.fields['assigned_doctor'].queryset = User.objects.filter(role='Doctor')
