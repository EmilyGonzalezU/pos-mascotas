import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.core.decorators import supervisor_required
from .services import MetricsService


@supervisor_required
def admin_dashboard(request):
    """Dashboard principal de administración con KPIs y gráficos."""
    tenant = getattr(request, 'tenant', None)
    if not tenant:
        return render(request, 'dashboard/no_tenant.html')

    service = MetricsService(tenant)
    summary = service.dashboard_summary()

    # Prepare chart data as JSON
    chart_data = {
        'labels': [d['label'] for d in summary['last_7_days']],
        'sales': [d['total'] for d in summary['last_7_days']],
        'orders': [d['count'] for d in summary['last_7_days']],
    }

    # Payment method labels
    method_labels = {
        'CASH': 'Efectivo',
        'CARD': 'Tarjeta',
        'TRANSFER': 'Transferencia',
        'MIXED': 'Mixto',
    }
    payment_chart = {
        'labels': [method_labels.get(p['method'], p['method']) for p in summary['payment_methods']],
        'values': [p['total'] for p in summary['payment_methods']],
    }

    return render(request, 'dashboard/admin_dashboard.html', {
        'summary': summary,
        'chart_data': json.dumps(chart_data),
        'payment_chart': json.dumps(payment_chart),
    })


@supervisor_required
def reports_margin(request):
    """Reporte de márgenes por producto."""
    tenant = getattr(request, 'tenant', None)
    service = MetricsService(tenant)
    margin_data = service.margin_report(days=30)

    return render(request, 'dashboard/reports_margin.html', {
        'margin_data': margin_data,
    })


@supervisor_required
def reports_top_products(request):
    """Top productos por ventas."""
    tenant = getattr(request, 'tenant', None)
    service = MetricsService(tenant)
    top = service.top_products(limit=20, days=30)

    return render(request, 'dashboard/reports_top_products.html', {
        'top_products': top,
    })


@supervisor_required
def alerts_stock(request):
    """Alertas de stock bajo."""
    tenant = getattr(request, 'tenant', None)
    service = MetricsService(tenant)
    low_stock = service.low_stock_alerts()
    expired = service.expired_batches()
    expiring = service.expiration_alerts(days=30)

    return render(request, 'dashboard/alerts_stock.html', {
        'low_stock': low_stock,
        'expired': expired,
        'expiring': expiring,
    })
