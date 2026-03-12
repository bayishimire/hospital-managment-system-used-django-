from django import forms
from .models import Consultation

class ConsultationForm(forms.ModelForm):
    class Meta:
        model = Consultation
        fields = [
            'symptoms', 'diagnosis', 'treatment_plan',
            'blood_pressure', 'temperature', 'heart_rate'
        ]
        widgets = {
            'symptoms': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter observed symptoms...'}),
            'diagnosis': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter medical diagnosis...'}),
            'treatment_plan': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter detailed treatment and recovery plan...'}),
            'blood_pressure': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 120/80'}),
            'temperature': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 37.5°C'}),
            'heart_rate': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 72 bpm'}),
        }
