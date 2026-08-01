from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views,api_views
router = DefaultRouter()
router.register(
    r'WEbondapplication',
    api_views.WageEarnersBondViewSet,
    basename='we-bond'
)
router.register(
    r'USDbondapplication',
    api_views.USDBondViewSet,
    basename='usd-bond'
)

urlpatterns = [
    # path('api/WEbondapplication/', api_views.WageEarnersBondViewSet, name="api_we_bond_application"),
    path("api/", include(router.urls)),
    # path("api/search_by_application_no/",
    #      api_views.search_by_application_no,
    #      name="search_by_application_no"),
    # new bond create
    path("new/",views.WageEarnersBondCreateView.as_view(),name="wage-earners-bond-create",),
    path("new-usd-Bond/",views.USDBondCreateView.as_view(),name="USD-bond-create",),
    path('success/<str:application_no>/', views.application_success, name='bond_application_success'),
    path('search/', views.search_application, name='search_bonds'),
    path('<str:application_no>/', views.bond_detail_public, name='application_detail_public'),
    path('<str:application_no>/process/', views.process_applicationBond, name='process_applicationBond'),
    path('<str:application_no>/print/', views.print_application, name='print_application_bonds'),
    path('<str:application_no>/print/html/', views.print_application_html, name="print_application_html"),
]