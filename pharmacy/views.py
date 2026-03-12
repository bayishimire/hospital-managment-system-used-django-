from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


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


from reception.models import PatientVisit
from django.utils import timezone

@login_required
@role_required('Pharmacy')
def dashboard(request):
    # Get patients waiting for Pharmacy
    queue = PatientVisit.objects.filter(status='Pharmacy').order_by('-priority', 'created_at')
    
    # Stats
    today = timezone.now().date()
    context = {
        'page_title': 'Pharmacy Dashboard',
        'role': 'Pharmacy',
        'user': request.user,
        'queue': queue,
        'stats': {
            'pending_prescriptions': queue.count(),
            'dispensed_today': PatientVisit.objects.filter(status='Discharged', updated_at__date=today).count(),
            'urgent_orders': queue.filter(priority__in=['Urgent', 'Emergency']).count(),
            'total_items': 450, # Mock stock level
        }
    }
    return render(request, 'pharmacy/dashboard.html', context)

@login_required
@role_required('Pharmacy')
def dispense_medication(request, fish_id):
    visit = PatientVisit.objects.get(fish_id=fish_id)
    if request.method == 'POST':
        # Mark as dispensed and discharge
        visit.status = 'Discharged'
        visit.save()
        messages.success(request, f"Medication for {visit.patient.first_name} dispensed. Patient discharged.")
        return redirect('pharmacy_dashboard')
    
    return render(request, 'pharmacy/dispense.html', {'visit': visit})
from django.shortcuts import get_object_or_404
from .models import Medication
from .forms import MedicationForm

@login_required
@role_required(['Pharmacy', 'Admin'])
def edit_medication(request, pk):
    med = get_object_or_404(Medication, pk=pk)
    if request.method == 'POST':
        form = MedicationForm(request.POST, instance=med)
        if form.is_valid():
            form.save()
            messages.success(request, f'Medication {med.name} updated successfully.')
            return redirect('pharmacy_monitor')
    else:
        form = MedicationForm(instance=med)
        
    return render(request, 'pharmacy/edit_medication.html', {
        'form': form,
        'med': med,
        'page_title': 'Audit Medication'
    })
