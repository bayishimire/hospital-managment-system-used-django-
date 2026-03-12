from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Patient
from .forms import PatientRegistrationForm

@login_required
def patient_list(request):
    if request.user.role != 'Admin' and not request.user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('redirect_dashboard')
    
    patients = Patient.objects.all().order_by('-created_at')
    return render(request, 'patients/patient_list.html', {
        'page_title': 'Patient Directory',
        'patients': patients,
    })

@login_required
def patient_edit(request, pk):
    if request.user.role != 'Admin' and not request.user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('redirect_dashboard')
        
    patient = get_object_or_404(Patient, pk=pk)
    form = PatientRegistrationForm(request.POST or None, request.FILES or None, instance=patient)
    
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, f'Records for {patient.first_name} updated successfully.')
            return redirect('patient_list')
            
    return render(request, 'patients/patient_edit.html', {
        'page_title': f'Edit Records: {patient.first_name}',
        'form': form,
        'patient': patient,
    })
