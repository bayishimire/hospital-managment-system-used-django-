from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import PatientVisit
from patients.models import Patient
from patients.forms import PatientRegistrationForm
from .forms import PatientVisitForm
from notifications.models import StaffNotification
from django.utils import timezone

def role_required(role_names):
    """Decorator factory to restrict views to multiple potential roles."""
    if isinstance(role_names, str):
        role_names = [role_names]
        
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.role not in role_names and not request.user.is_superuser:
                messages.error(request, f'Access denied. This area is for {role_names} staff only.')
                return redirect('redirect_dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
@login_required
@role_required('Reception')
def dashboard(request):
    # Handle Registration
    reg_form = PatientRegistrationForm()
    visit_form = PatientVisitForm()

    if request.method == 'POST':
        if 'register_patient' in request.POST:
            reg_form = PatientRegistrationForm(request.POST)
            if reg_form.is_valid():
                patient = reg_form.save()
                messages.success(request, f'Patient {patient.first_name} registered successfully. ID: {patient.patient_id}')
                return redirect('reception_dashboard')
        
        elif 'create_visit' in request.POST:
            visit_form = PatientVisitForm(request.POST)
            if visit_form.is_valid():
                visit = visit_form.save()
                
                # Notify the doctor
                if visit.assigned_doctor:
                    StaffNotification.objects.create(
                        recipient=visit.assigned_doctor,
                        title="New Patient Arrived",
                        message=f"Patient {visit.patient.first_name} {visit.patient.last_name} is waiting for you. Fish ID: {visit.fish_id}",
                    )
                
                messages.success(request, f'Patient {visit.patient.first_name} assigned to Doctor {visit.assigned_doctor.get_full_name()}.')
                return redirect('reception_dashboard')

    # Get Queue
    queue = PatientVisit.objects.filter(status__in=['Waiting', 'Consulting', 'Lab', 'Pharmacy']).order_by('-priority', 'created_at')
    
    # Stats
    today = timezone.now().date()
    context = {
        'page_title': 'Reception Dashboard',
        'role': 'Reception',
        'user': request.user,
        'reg_form': reg_form,
        'visit_form': visit_form,
        'queue': queue,
        'stats': {
            'today_registrations': Patient.objects.filter(created_at__date=today).count(),
            'waiting_queue': PatientVisit.objects.filter(status='Waiting').count(),
            'total_patients': Patient.objects.count(),
            'urgent_cases': PatientVisit.objects.filter(priority__in=['Urgent', 'Emergency'], status='Waiting').count(),
        }
    }
    return render(request, 'reception/dashboard.html', context)

@login_required
@role_required(['Reception', 'Admin'])
def edit_visit(request, pk):
    visit = PatientVisit.objects.get(pk=pk)
    if request.method == 'POST':
        form = PatientVisitForm(request.POST, instance=visit)
        if form.is_valid():
            form.save()
            messages.success(request, f'Visit {visit.fish_id} updated successfully.')
            return redirect('reception_dashboard')
    else:
        form = PatientVisitForm(instance=visit)
    
    return render(request, 'reception/edit_visit.html', {
        'form': form,
        'visit': visit,
        'page_title': 'Edit Patient Visit'
    })

@login_required
@role_required(['Reception', 'Admin'])
def delete_visit(request, pk):
    visit = PatientVisit.objects.get(pk=pk)
    if request.method == 'POST':
        fish_id = visit.fish_id
        visit.delete()
        messages.success(request, f'Visit {fish_id} has been cancelled and removed from the queue.')
    return redirect('reception_dashboard')
