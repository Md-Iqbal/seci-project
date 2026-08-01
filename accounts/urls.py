from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, api_views

# DRF Router
router = DefaultRouter()
router.register(r'applications', api_views.AccountApplicationViewSet, basename='application')

urlpatterns = [
    # API URLs
    path('api/', include(router.urls)),
    
    path('api/dashboard-stats/', api_views.dashboard_stats, name='api_dashboard_stats'),
    
    # Public URLs
    path('', views.home, name='home'),
    path('apply/', views.apply_account, name='apply_account'),
    path('success/<str:app_number>/', views.application_success, name='application_success'),
    path('search/', views.search_application, name='search_application'),
    path('application/<str:app_number>/', views.application_detail_public, name='application_detail_public'),
    
    # Employee URLs
    path('login/', views.custom_login, name='login'),
    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('applications/', views.application_list, name='application_list'),
    path('applications/<str:app_number>/detail/', views.application_detail, name='application_detail'),
    path('applications/<str:app_number>/process/', views.process_application, name='process_application'),
    path('applications/<str:app_number>/print/', views.print_application, name='print_application'),
]

# API URLs - these will be prefixed with /api/ in main urls.py
# api_urlpatterns = [
#     # path('', include(router.urls)),
#     # path('dashboard-stats/', api_views.dashboard_stats, name='api_dashboard_stats'),
# ]
