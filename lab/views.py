from django.shortcuts import render, redirect, get_object_or_404
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
@role_required('Lab')
def dashboard(request):
    # Get patients waiting for Lab
    queue = PatientVisit.objects.filter(status='Lab').order_by('-priority', 'created_at')
    
    # Stats
    today = timezone.now().date()
    context = {
        'page_title': 'Laboratory Dashboard',
        'role': 'Lab',
        'user': request.user,
        'queue': queue,
        'stats': {
            'pending_tests': queue.count(),
            'urgent_tests': queue.filter(priority__in=['Urgent', 'Emergency']).count(),
            'completed_today': PatientVisit.objects.filter(status__in=['Pharmacy', 'Discharged'], updated_at__date=today).count(),
            'total_processed': PatientVisit.objects.filter(updated_at__date=today).count(),
        }
    }
    return render(request, 'lab/dashboard.html', context)

from notifications.models import StaffNotification

@login_required
@role_required('Lab')
def complete_lab(request, fish_id):
    visit = PatientVisit.objects.get(fish_id=fish_id)
    if request.method == 'POST':
        results = request.POST.get('results', '')
        status_conclusion = request.POST.get('status_conclusion', '')
        
        # Update Pending LabOrders for this visit
        lab_orders = visit.lab_orders.filter(status='Pending')
        for order in lab_orders:
            order.status = 'Completed'
            order.results = f"[{status_conclusion}] {results}"
            order.save()

        visit.status = 'Consulting' # Send back to doctor
        visit.save()
        
        # Notify the referring doctor automatically
        if visit.assigned_doctor:
            StaffNotification.objects.create(
                recipient=visit.assigned_doctor,
                title='Lab Results Ready',
                message=f"Lab tests completed for {visit.patient.first_name} {visit.patient.last_name} ({visit.fish_id}). Result: {status_conclusion}."
            )

        messages.success(request, f"Lab results for {visit.patient.first_name} completed. Notification sent back to Doctor.")
        return redirect('lab_dashboard')
    
    return render(request, 'lab/record_results.html', {'visit': visit})
from .models import LabOrder
from .forms import LabOrderForm

@login_required
@role_required(['Lab', 'Admin'])
def edit_lab_order(request, pk):
    order = get_object_or_404(LabOrder, pk=pk)
    if request.method == 'POST':
        form = LabOrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, f'Lab Order #{order.id} updated.')
            return redirect('lab_monitor')
    else:
        form = LabOrderForm(instance=order)
    
    return render(request, 'lab/edit_order.html', {
        'form': form,
        'order': order,
        'page_title': 'Audit Lab Order'
    })
