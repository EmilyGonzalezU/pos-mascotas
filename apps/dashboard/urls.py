from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('reports/margin/', views.reports_margin, name='reports_margin'),
    path('reports/top-products/', views.reports_top_products, name='reports_top_products'),
    path('alerts/stock/', views.alerts_stock, name='alerts_stock'),
]
