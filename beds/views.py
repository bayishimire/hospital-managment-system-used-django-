from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Ward, Bed

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
@role_required('WardManager')
def dashboard(request):
    wards = Ward.objects.all()
    beds = Bed.objects.all()
    
    occupied_count = beds.filter(is_occupied=True).count()
    available_count = beds.filter(is_occupied=False).count()
    
    context = {
        'page_title': 'Bed Management',
        'role': 'WardManager',
        'user': request.user,
        'wards': wards,
        'beds': beds,
        'stats': {
            'total_beds': beds.count(),
            'occupied_beds': occupied_count,
            'available_beds': available_count,
        }
    }
    return render(request, 'beds/dashboard.html', context)

@login_required
def manage_beds(request):
    """Admin/WardManager suite for hospital infrastructure."""
    if request.user.role != 'Admin' and request.user.role != 'WardManager' and not request.user.is_superuser:
        return redirect('redirect_dashboard')
    
    from .forms import WardForm, BedForm
    wards = Ward.objects.all().order_by('name')
    beds = Bed.objects.all().order_by('ward__name', 'bed_number')
    
    ward_form = WardForm(request.POST or None)
    bed_form = BedForm(request.POST or None)
    
    if request.method == 'POST':
        if 'add_ward' in request.POST:
            if ward_form.is_valid():
                ward_form.save()
                messages.success(request, 'New Ward created successfully.')
                return redirect('manage_beds')
        elif 'add_bed' in request.POST:
            if bed_form.is_valid():
                bed_form.save()
                messages.success(request, 'New Bed registered successfully.')
                return redirect('manage_beds')

    return render(request, 'beds/manage_beds.html', {
        'page_title': 'Ward & Bed Control',
        'wards': wards,
        'beds': beds,
        'ward_form': ward_form,
        'bed_form': bed_form,
    })
from django.shortcuts import get_object_or_404
from .forms import WardForm, BedForm

@login_required
def edit_ward(request, pk):
    """Edit an existing Ward."""
    if request.user.role not in ['Admin', 'WardManager'] and not request.user.is_superuser:
        return redirect('redirect_dashboard')
    ward = get_object_or_404(Ward, pk=pk)
    form = WardForm(request.POST or None, instance=ward)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Ward "{ward.name}" updated successfully.')
        return redirect('manage_beds')
    return render(request, 'beds/edit_ward.html', {
        'form': form,
        'ward': ward,
        'page_title': f'Edit Ward: {ward.name}',
    })

@login_required
def edit_bed(request, pk):
    """Edit an existing Bed."""
    if request.user.role not in ['Admin', 'WardManager'] and not request.user.is_superuser:
        return redirect('redirect_dashboard')
    bed = get_object_or_404(Bed, pk=pk)
    form = BedForm(request.POST or None, instance=bed)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Bed {bed.bed_number} updated successfully.')
        return redirect('manage_beds')
    return render(request, 'beds/edit_bed.html', {
        'form': form,
        'bed': bed,
        'page_title': f'Edit Bed: {bed.bed_number}',
    })
