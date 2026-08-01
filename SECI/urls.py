from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API URLs
    # path('api/', include('accounts.urls')),
    
    # Accounts app URLs
    path('', include('accounts.urls')),
    path('bonds/', include('bonds.urls')),
    
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(
        template_name='accounts/login.html',
        redirect_authenticated_user=True,
        extra_context={'next': 'dashboard'}
    ), name='login'),
    
    path('logout/', auth_views.LogoutView.as_view(
        next_page='home'
    ), name='logout'),
    
    # Redirect /accounts/profile/ to dashboard (Django's default login redirect)
    path('accounts/profile/', RedirectView.as_view(
        pattern_name='dashboard',
        permanent=False
    )),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin site customization
admin.site.site_header = "সোনালী ব্যাংক পিএলসি - প্রশাসন"
admin.site.site_title = "সোনালী ব্যাংক প্রশাসন"
admin.site.index_title = "প্রশাসনিক ড্যাশবোর্ডে স্বাগতম"