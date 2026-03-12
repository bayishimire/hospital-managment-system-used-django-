from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def role_required(role_name):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.role != role_name and not request.user.is_superuser:
                messages.error(request, f'Access denied. This area is for {role_name} staff only.')
                return redirect('redirect_dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


from reception.models import PatientVisit
from notifications.models import StaffNotification
from .models import Consultation
from django.utils import timezone

@login_required
@role_required('Doctor')
def dashboard(request):
    """Premium clinical portal for hospital doctors."""
    # Get unread notifications
    unread_notifications = StaffNotification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]
    
    # Get active patients assigned to this doctor (The Fish Stream)
    active_patients = PatientVisit.objects.filter(
        assigned_doctor=request.user,
        status__in=['Waiting', 'Consulting', 'Lab', 'Pharmacy', 'Admitted']
    ).order_by('-priority', '-created_at')
    
    today = timezone.now().date()
    stats = {
        'todays_total': PatientVisit.objects.filter(assigned_doctor=request.user, created_at__date=today).count(),
        'waiting_count': PatientVisit.objects.filter(assigned_doctor=request.user, status='Waiting').count(),
        'active_treated': PatientVisit.objects.filter(assigned_doctor=request.user, status='Consulting').count(),
        'admitted_under_me': PatientVisit.objects.filter(assigned_doctor=request.user, status='Admitted').count(),
    }
    
    context = {
        'page_title': "Clinical Portal",
        'role': 'Doctor',
        'user': request.user,
        'notifications': unread_notifications,
        'patients': active_patients,
        'stats': stats,
        'now': timezone.now(),
    }
    return render(request, 'doctors/dashboard.html', context)

from .forms import ConsultationForm

from lab.models import LabOrder
from pharmacy.models import Prescription
from beds.models import Bed

@login_required
@role_required('Doctor')
def start_treatment(request, fish_id):
    """Clinical intake and management interface (The Fish)."""
    visit = PatientVisit.objects.get(fish_id=fish_id)
    
    if visit.assigned_doctor != request.user and not request.user.is_superuser:
        messages.error(request, "Security Alert: This record is assigned to another professional.")
        return redirect('doctor_dashboard')
    
    if visit.status == 'Waiting':
        visit.status = 'Consulting'
        visit.save()
    
    consultation, created = Consultation.objects.get_or_create(visit=visit)
    form = ConsultationForm(instance=consultation)
    
    # Fetch existing orders
    lab_orders = visit.lab_orders.all()
    prescriptions = visit.prescriptions.all()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        # 1. Update Clinical Record
        if action == 'save_notes':
            form = ConsultationForm(request.POST, instance=consultation)
            if form.is_valid():
                form.save()
                messages.success(request, "Clinical notes saved successfully.")
            else:
                messages.error(request, "Error validating clinical data.")

        # 2. Digital Lab Order
        elif action == 'create_lab_order':
            test_name = request.POST.get('test_name')
            if test_name:
                LabOrder.objects.create(visit=visit, test_name=test_name, status='Pending')
                visit.status = 'Lab'
                visit.save()
                messages.success(request, f"Lab order issued: {test_name}")
                return redirect('doctor_dashboard')

        # 3. Electronic Prescription
        elif action == 'create_prescription':
            med = request.POST.get('med_name')
            if med:
                Prescription.objects.create(
                    visit=visit, 
                    medication_name=med, 
                    dosage=request.POST.get('dosage'),
                    frequency=request.POST.get('freq'),
                    duration=request.POST.get('dur')
                )
                visit.status = 'Pharmacy'
                visit.save()
                messages.success(request, f"Prescription authorized: {med}")
                return redirect('doctor_dashboard')

        # 4. Bed Assignment & Admission
        elif action == 'admit_patient':
            bed_id = request.POST.get('bed_id')
            if bed_id:
                bed = Bed.objects.get(id=bed_id)
                bed.is_occupied = True
                bed.current_patient = visit.patient
                bed.save()
                visit.status = 'Admitted'
                visit.save()
                messages.success(request, f"Patient admitted to {bed}")
                return redirect('doctor_dashboard')

        # 5. Urgent Alert
        elif action == 'set_urgent':
            visit.priority = 'Urgent'
            visit.save()
            messages.warning(request, "Urgent alert marked on patient file.")

        # 6. Forward to Billing
        elif action == 'forward_billing':
            visit.status = 'Billing'
            visit.save()
            messages.info(request, "Patient file forwarded to Finance for billing.")
            return redirect('doctor_dashboard')

        return redirect('start_treatment', fish_id=fish_id)
    
    # Available beds for admission
    available_beds = Bed.objects.filter(is_occupied=False)

    context = {
        'visit': visit,
        'consultation': consultation,
        'patient': visit.patient,
        'form': form,
        'lab_orders': lab_orders,
        'prescriptions': prescriptions,
        'available_beds': available_beds,
        'page_title': f"Clinical Fish: {visit.patient.first_name}"
    }
    return render(request, 'doctors/consultation.html', context)

@login_required
def mark_notification_read(request, notif_id):
    try:
        notif = StaffNotification.objects.get(id=notif_id, recipient=request.user)
        notif.is_read = True
        notif.save()
    except StaffNotification.DoesNotExist:
        pass
    return redirect('doctor_dashboard')

from django.db.models import Q

@login_required
@role_required('Doctor')
def patient_search(request):
    query = request.GET.get('q', '')
    results = None
    if query:
        results = PatientVisit.objects.filter(
            Q(fish_id__icontains=query) |
            Q(patient__patient_id__icontains=query) |
            Q(patient__first_name__icontains=query) |
            Q(patient__last_name__icontains=query)
        ).order_by('-created_at')[:20]
    return render(request, 'doctors/patient_search.html', {'query': query, 'results': results})

@login_required
@role_required('Doctor')
def my_appointments(request):
    today = timezone.now().date()
    appointments = PatientVisit.objects.filter(
        assigned_doctor=request.user, 
        created_at__date=today
    ).order_by('created_at')
    return render(request, 'doctors/my_appointments.html', {'appointments': appointments})

@login_required
@role_required('Doctor')
def medical_library(request):
    return render(request, 'doctors/medical_library.html')
