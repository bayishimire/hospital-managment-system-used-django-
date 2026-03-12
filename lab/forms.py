from django import forms
from .models import LabOrder

class LabOrderForm(forms.ModelForm):
    class Meta:
        model = LabOrder
        fields = ['visit', 'test_name', 'instructions', 'status', 'results']
        widgets = {
            'visit': forms.Select(attrs={'class': 'form-select'}),
            'test_name': forms.TextInput(attrs={'class': 'form-control'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'results': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
