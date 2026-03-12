from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .forms import LoginForm, RegisterForm


# ─── Role → dashboard URL mapping ───────────────────────────────────────────
ROLE_REDIRECT = {
    'Doctor':    '/doctor/dashboard/',
    'Reception': '/reception/dashboard/',
    'Lab':       '/lab/dashboard/',
    'Pharmacy':  '/pharmacy/dashboard/',
    'Payments':  '/payments/dashboard/',
    'Admin':     '/accounts/admin-panel/dashboard/',   # Custom HMS admin dashboard
}


def home(request):
    """Public hospital welcome / landing page."""
    return render(request, 'home.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('redirect_dashboard')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('redirect_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required
def redirect_dashboard(request):
    """Redirect authenticated users to their role-based dashboard."""
    user = request.user
    url = ROLE_REDIRECT.get(user.role)
    if url:
        return redirect(url)
    # Superuser with no specific role → Django admin
    if user.is_superuser or user.is_staff:
        return redirect('/admin/')
    # Fallback
    return render(request, 'accounts/no_role.html')


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})


@login_required
def admin_dashboard(request):
    """Full-scale Mission Control for hospital administrators."""
    user = request.user
    if user.role != 'Admin' and not user.is_superuser:
        messages.error(request, 'Access denied. Admin area only.')
        return redirect('redirect_dashboard')

    from django.contrib.auth import get_user_model
    from django.contrib.admin.models import LogEntry
    from django.db.models import Count, Sum, F
    from django.db.models.functions import TruncDate
    from pharmacy.models import Medication
    from beds.models import Bed
    from lab.models import LabOrder
    from payments.models import Payment
    from reception.models import PatientVisit
    from patients.models import Patient
    import json
    
    User = get_user_model()
    
    # Handle Staff Registration / Updates
    reg_form = RegisterForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and 'register_staff' in request.POST:
        if reg_form.is_valid():
            new_staff = reg_form.save()
            messages.success(request, f"Registered {new_staff.get_full_name()} as {new_staff.role}.")
            return redirect('admin_dashboard')

    # 1. Human Resources
    stats = {
        'total_users':      User.objects.count(),
        'doctors_on_duty':  User.objects.filter(role='Doctor', is_on_duty=True).count(),
        'nurses':           User.objects.filter(role='Nurse').count(),
        'admins':           User.objects.filter(role='Admin').count(),
    }

    # 2. Clinical & Operational Monitoring
    monitor = {
        'pending_lab':      LabOrder.objects.filter(status='Pending').count(),
        'low_stock':        Medication.objects.filter(stock_quantity__lte=F('low_stock_threshold')).count(),
        'available_beds':   Bed.objects.filter(is_occupied=False).count(),
        'pending_payments': Payment.objects.filter(status='Pending').count(),
        'total_revenue':    Payment.objects.filter(status='Paid').aggregate(Sum('amount'))['amount__sum'] or 0,
        'today_patients':   PatientVisit.objects.filter(created_at__date=timezone.now().date()).count(),
    }

    # 3. Chart Data: Patient Flow (Last 10 days histogram)
    last_10_days = timezone.now() - timezone.timedelta(days=10)
    patient_flow = PatientVisit.objects.filter(created_at__gte=last_10_days)\
        .annotate(date=TruncDate('created_at'))\
        .values('date')\
        .annotate(count=Count('id'))\
        .order_by('date')
    
    chart_flow = {
        'labels': [d['date'].strftime('%d %b') for d in patient_flow],
        'counts': [d['count'] for d in patient_flow]
    }

    # 4. Chart Data: Department Performance (Lab vs Pharmacy vs Consult)
    performance = {
        'labels': ['Consultation', 'Laboratory', 'Pharmacy'],
        'counts': [
            PatientVisit.objects.filter(status='Waiting').count(),
            LabOrder.objects.count(),
            Medication.objects.aggregate(Sum('stock_quantity'))['stock_quantity__sum'] or 0 # Example metric
        ]
    }

    # System Activity & Recent Users
    activity_qs = LogEntry.objects.select_related('user', 'content_type').order_by('-action_time')[:50]
    recent_users = User.objects.order_by('-created_at')[:6]

    # =========================================================
    # ADVANCED ANALYTICS (Pandas + Matplotlib Base64 Encoding)
    # =========================================================
    import pandas as pd
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import io
    import urllib, base64

    chart_hist_uri = None
    chart_bar_uri = None

    if activity_qs.exists():
        # Build a DataFrame of recent activities
        data = []
        for a in activity_qs:
            data.append({
                'time': a.action_time,
                'user': a.user.username if a.user else 'System',
                'action_flag': a.action_flag,
                'content_type': a.content_type.name if a.content_type else 'Unknown'
            })
        
        df = pd.DataFrame(data)
        
        # --- 1. Histogram of Activities over time ---
        plt.figure(figsize=(7, 3.5), facecolor='#ffffff')
        ax = plt.axes()
        ax.set_facecolor('#ffffff')
        
        # Plot histogram of action times (hour bins)
        df['time'].dt.hour.plot(kind='hist', bins=24, color='#2980b9', edgecolor='white', alpha=0.8)
        
        plt.title('Activity Histogram (24H Distribution)', color='#1e3a5f', fontsize=10, fontweight='bold')
        plt.xlabel('Hour of Day', color='#4a6fa5', fontsize=8)
        plt.ylabel('Activity Count', color='#4a6fa5', fontsize=8)
        plt.xticks(range(0, 24, 2), color='#4a6fa5', fontsize=8)
        plt.yticks(color='#4a6fa5', fontsize=8)
        
        # Styling the spines
        for spine in ['top', 'right']:
            ax.spines[spine].set_visible(False)
        for spine in ['bottom', 'left']:
            ax.spines[spine].set_color('#d0e3f5')

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', transparent=True)
        buf.seek(0)
        string = base64.b64encode(buf.read())
        chart_hist_uri = 'data:image/png;base64,' + urllib.parse.quote(string)
        plt.close()

        # --- 2. Bar Chart of Content Types Modified ---
        plt.figure(figsize=(7, 3.5), facecolor='#ffffff')
        ax2 = plt.axes()
        ax2.set_facecolor('#ffffff')
        
        model_counts = df['content_type'].value_counts().head(6)
        
        bars = model_counts.plot(kind='bar', color='#1a6696', edgecolor='none')
        
        plt.title('Most Modified Models', color='#1e3a5f', fontsize=10, fontweight='bold')
        plt.xlabel('Module', color='#4a6fa5', fontsize=8)
        plt.ylabel('Changes', color='#4a6fa5', fontsize=8)
        plt.xticks(rotation=15, color='#4a6fa5', fontsize=8)
        plt.yticks(color='#4a6fa5', fontsize=8)
        
        for spine in ['top', 'right']:
            ax2.spines[spine].set_visible(False)
        for spine in ['bottom', 'left']:
            ax2.spines[spine].set_color('#d0e3f5')

        plt.tight_layout()
        buf2 = io.BytesIO()
        plt.savefig(buf2, format='png', dpi=100, bbox_inches='tight', transparent=True)
        buf2.seek(0)
        string2 = base64.b64encode(buf2.read())
        chart_bar_uri = 'data:image/png;base64,' + urllib.parse.quote(string2)
        plt.close()

    # Pass the Base64 images to the template context
    return render(request, 'admin_panel/dashboard.html', {
        'page_title': 'Mission Control',
        'matplotlib_hist': chart_hist_uri,
        'matplotlib_bar': chart_bar_uri,
        'role': 'Admin',
        'user': user,
        'stats': stats,
        'monitor': monitor,
        'recent_users': recent_users,
        'activity': activity_qs,
        'reg_form': reg_form,
        'charts': {
            'flow': json.dumps(chart_flow),
            'perf': json.dumps(performance),
        }
    })


@login_required
def staff_management(request):
    """Bespoke management suite for hospital personnel and onboarding."""
    user = request.user
    if user.role != 'Admin' and not user.is_superuser:
        messages.error(request, 'Access denied. Administrative authority required.')
        return redirect('redirect_dashboard')

    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # Handle Personnel Registration
    reg_form = RegisterForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and 'register_staff' in request.POST:
        if reg_form.is_valid():
            new_staff = reg_form.save()
            messages.success(request, f"Successfully authorized {new_staff.get_full_name() or new_staff.username} as {new_staff.role}.")
            return redirect('staff_management')
        else:
            messages.error(request, 'Authorization failed. Please verify credentials.')

    # Fetch all staff members
    staff_list = User.objects.all().order_by('-created_at')

    return render(request, 'accounts/staff_management.html', {
        'page_title': 'Staff Management',
        'staff_list': staff_list,
        'reg_form': reg_form,
    })


@login_required
def register_view(request):
    """Dedicated professional registration page with manual HTML."""
    user = request.user
    if user.role != 'Admin' and not user.is_superuser:
        messages.error(request, 'Access denied. Administrative authority required.')
        return redirect('redirect_dashboard')

    reg_form = RegisterForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if reg_form.is_valid():
            new_user = reg_form.save()
            messages.success(request, f"Professional account for {new_user.get_full_name()} created successfully.")
            return redirect('staff_management')
        else:
            messages.error(request, "Registration failed. Please check the details provided.")

    return render(request, 'accounts/register.html', {
        'page_title': 'Register Professional',
        'reg_form': reg_form,
    })
@login_required
def clinical_monitor(request):
    """Bespoke monitor for clinical operations."""
    if request.user.role != 'Admin' and not request.user.is_superuser:
        return redirect('redirect_dashboard')
    
    from reception.models import PatientVisit
    visits = PatientVisit.objects.all().order_by('-created_at')
    
    return render(request, 'admin_panel/clinical_monitor.html', {
        'page_title': 'Clinical Audit',
        'visits': visits,
    })

@login_required
def lab_monitor(request):
    """Bespoke monitor for laboratory operations."""
    if request.user.role != 'Admin' and not request.user.is_superuser:
        return redirect('redirect_dashboard')
    
    from lab.models import LabOrder
    orders = LabOrder.objects.all().order_by('-id')
    
    return render(request, 'admin_panel/lab_monitor.html', {
        'page_title': 'Laboratory Audit',
        'orders': orders,
    })

@login_required
def pharmacy_monitor(request):
    """Bespoke monitor for pharmacy operations."""
    if request.user.role != 'Admin' and not request.user.is_superuser:
        return redirect('redirect_dashboard')
    
    from pharmacy.models import Medication
    meds = Medication.objects.all().order_by('name')
    
    return render(request, 'admin_panel/pharmacy_monitor.html', {
        'page_title': 'Pharmacy Audit',
        'meds': meds,
    })

@login_required
def finance_monitor(request):
    """Bespoke monitor for financial operations."""
    if request.user.role != 'Admin' and not request.user.is_superuser:
        return redirect('redirect_dashboard')
    
    from payments.models import Payment
    payments = Payment.objects.all().order_by('-id')
    
    return render(request, 'admin_panel/finance_monitor.html', {
        'page_title': 'Finance Audit',
        'payments': payments,
    })


@login_required
def edit_staff(request, pk):
    """Admin-only: edit a staff member's profile."""
    if request.user.role != 'Admin' and not request.user.is_superuser:
        messages.error(request, 'Access denied. Administrative authority required.')
        return redirect('redirect_dashboard')
    
    from django.contrib.auth import get_user_model
    from django.shortcuts import get_object_or_404
    User = get_user_model()
    staff = get_object_or_404(User, pk=pk)
    
    # Re-use RegisterForm but only update safe fields
    from .forms import RegisterForm
    
    if request.method == 'POST':
        # Manually update editable fields only
        staff.first_name = request.POST.get('first_name', staff.first_name)
        staff.last_name  = request.POST.get('last_name', staff.last_name)
        staff.phone      = request.POST.get('phone', staff.phone)
        staff.role       = request.POST.get('role', staff.role)
        if request.FILES.get('profile_photo'):
            staff.profile_photo = request.FILES['profile_photo']
        staff.save()
        messages.success(request, f'{staff.get_full_name() or staff.username} updated successfully.')
        return redirect('admin_dashboard')
    
    return render(request, 'accounts/edit_staff.html', {
        'page_title': f'Edit Staff: {staff.get_full_name() or staff.username}',
        'staff': staff,
        'role_choices': ['Admin', 'Doctor', 'Reception', 'Lab', 'Pharmacy', 'Payments', 'WardManager'],
    })


@login_required
def delete_staff(request, pk):
    """Admin-only: delete a staff member."""
    if request.user.role != 'Admin' and not request.user.is_superuser:
        messages.error(request, 'Access denied. Administrative authority required.')
        return redirect('redirect_dashboard')
    
    from django.contrib.auth import get_user_model
    from django.shortcuts import get_object_or_404
    User = get_user_model()
    staff = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        if staff == request.user:
            messages.error(request, 'You cannot delete your own account.')
            return redirect('admin_dashboard')
        name = staff.get_full_name() or staff.username
        staff.delete()
        messages.success(request, f'Staff member "{name}" removed from the system.')
        return redirect('admin_dashboard')
    
    return redirect('admin_dashboard')
