from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Username',
            'id': 'username',
            'autofocus': True,
        }),
        label='Username',
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Password',
            'id': 'password',
        }),
        label='Password',
    )


class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create password',
        }),
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password',
        }),
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'role', 'phone', 'department', 'employee_id', 'profile_photo']
        widgets = {
            'first_name':   forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'username':     forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username'}),
            'email':        forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'}),
            'role':         forms.Select(attrs={'class': 'form-select'}),
            'phone':        forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
            'department':   forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Department (e.g. Cardiology)'}),
            'employee_id':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Staff / Employee ID'}),
            'profile_photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Passwords do not match.')
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user
