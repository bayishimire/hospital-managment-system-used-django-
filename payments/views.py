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

@login_required
@role_required('Payments')
def dashboard(request):
    billing_queue = PatientVisit.objects.filter(status='Billing').order_by('created_at')

    context = {
        'page_title': 'Payments & Finance',
        'role': 'Payments',
        'user': request.user,
        'queue': billing_queue,
        'stats': {
            'todays_revenue': '0.00',
            'pending_payments': billing_queue.count(),
            'insurance_claims': 0,
            'paid_today': 0,
        }
    }
    return render(request, 'payments/dashboard.html', context)
from django.shortcuts import get_object_or_404
from .models import Payment
from .forms import PaymentForm

@login_required
@role_required(['Payments', 'Admin'])
def edit_payment(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            form.save()
            messages.success(request, f'Payment for {payment.visit.fish_id} updated.')
            return redirect('finance_monitor')
    else:
        form = PaymentForm(instance=payment)
        
    return render(request, 'payments/edit_payment.html', {
        'form': form,
        'payment': payment,
        'page_title': 'Audit Payment'
    })


@login_required
@role_required('Payments')
def process_payment(request, fish_id):
    visit = get_object_or_404(PatientVisit, fish_id=fish_id, status='Billing')
    if request.method == 'POST':
        amount = request.POST.get('amount', 0)
        method = request.POST.get('method', 'Cash')
        
        # Create payment record
        Payment.objects.create(
            visit=visit,
            amount=amount,
            method=method,
            status='Paid',
            collected_by=request.user
        )
        
        # Discharge patient
        visit.status = 'Discharged'
        visit.save()
        
        messages.success(request, f'Payment of RWF {amount} processed. Patient {visit.patient.first_name} is discharged.')
        return redirect('payments_dashboard')
        
    # Calculate dummy costs for now, ideally fetch from LabOrder/Pharmacy
    pharmacy_cost = 2500
    consult_cost = 5000
    lab_cost = 3000
    bed_cost = 0
    total = pharmacy_cost + consult_cost + lab_cost + bed_cost
    
    return render(request, 'payments/process.html', {
        'visit': visit,
        'pharmacy_cost': pharmacy_cost,
        'consult_cost': consult_cost,
        'lab_cost': lab_cost,
        'bed_cost': bed_cost,
        'total': total,
        'page_title': 'Process Payment'
    })


@login_required
@role_required('Payments')
def insurance_claim(request, fish_id):
    visit = get_object_or_404(PatientVisit, fish_id=fish_id, status='Billing')
    
    # Fast track insurance processing
    amount = 10500 # standard claim amount
    Payment.objects.create(
        visit=visit,
        amount=amount,
        method='Insurance',
        status='Paid',
        collected_by=request.user
    )
    
    visit.status = 'Discharged'
    visit.save()
    
    messages.success(request, f'Insurance Claim processed. Patient {visit.patient.first_name} is discharged.')
    return redirect('payments_dashboard')


@login_required
@role_required('Payments')
def print_receipt(request, fish_id):
    visit = get_object_or_404(PatientVisit, fish_id=fish_id)
    payment = visit.payments.filter(status='Paid').first()
    
    return render(request, 'payments/receipt.html', {
        'visit': visit,
        'payment': payment,
        'page_title': 'Print Receipt'
    })

@login_required
@role_required(['Payments', 'Admin'])
def view_report(request):
    from django.db.models import Sum
    from django.utils import timezone
    today = timezone.now().date()
    payments_today = Payment.objects.filter(created_at__date=today, status='Paid')
    total_rev = payments_today.aggregate(Sum('amount'))['amount__sum'] or 0

    return render(request, 'payments/report.html', {
        'payments': payments_today,
        'total_rev': total_rev,
        'page_title': 'Daily Revenue Report'
    })
