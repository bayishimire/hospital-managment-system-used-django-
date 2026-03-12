from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts import views as account_views

urlpatterns = [
    # Custom Admin Dashboard as the primary entry point
    path('admin/', account_views.admin_dashboard),
    path('admin/', admin.site.urls),
    # Home page at root
    path('', account_views.home, name='home'),
    # All account/auth URLs under /accounts/
    path('accounts/', include('accounts.urls')),
    # Department dashboards
    path('reception/', include('reception.urls')),
    path('doctor/', include('doctors.urls')),
    path('lab/', include('lab.urls')),
    path('pharmacy/', include('pharmacy.urls')),
    path('payments/', include('payments.urls')),
    path('beds/', include('beds.urls')),
    path('patients/', include('patients.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
