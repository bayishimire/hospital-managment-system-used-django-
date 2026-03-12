from django import forms
from .models import Patient

class PatientRegistrationForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'gender',
            'phone', 'email', 'address', 'emergency_contact_name',
            'emergency_contact_phone', 'insurance_provider', 
            'insurance_policy_number', 'is_insurance_verified', 'verification_notes'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email (Optional)'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Home Address'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Emergency Contact Name'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Emergency Contact Phone'}),
            'insurance_provider': forms.Select(attrs={'class': 'form-select'}),
            'insurance_policy_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Policy Number'}),
            'is_insurance_verified': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'verification_notes': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Verification notes/details...'}),
        }
