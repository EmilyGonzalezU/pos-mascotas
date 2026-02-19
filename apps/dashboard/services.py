"""
MetricsService — Calcula métricas para el dashboard administrativo.
Toda la lógica de reportes se centraliza aquí, fuera de las views.
"""
from datetime import date, timedelta
from decimal import Decimal
from django.db.models import Sum, Count, F, Q
from django.utils import timezone

from apps.sales.models import Order, OrderItem, Payment, Shift
from apps.inventory.models import Product, Batch


class MetricsService:
    """Calcula métricas de ventas, inventario y operaciones."""

    def __init__(self, tenant, branch=None):
        self.tenant = tenant
        self.branch = branch

    def _base_orders(self):
        qs = Order.all_objects.filter(
            tenant=self.tenant, is_paid=True, is_voided=False,
        )
        if self.branch:
            qs = qs.filter(branch=self.branch)
        return qs

    # ──────────── Sales metrics ────────────

    def sales_today(self):
        today = timezone.now().date()
        qs = self._base_orders().filter(date__date=today)
        result = qs.aggregate(total=Sum('total_clp'), count=Count('id'))
        return {
            'total': result['total'] or 0,
            'count': result['count'] or 0,
        }

    def sales_this_week(self):
        today = timezone.now().date()
        start = today - timedelta(days=today.weekday())  # Monday
        qs = self._base_orders().filter(date__date__gte=start)
        result = qs.aggregate(total=Sum('total_clp'), count=Count('id'))
        return {
            'total': result['total'] or 0,
            'count': result['count'] or 0,
        }

    def sales_this_month(self):
        today = timezone.now()
        qs = self._base_orders().filter(
            date__year=today.year, date__month=today.month,
        )
        result = qs.aggregate(total=Sum('total_clp'), count=Count('id'))
        return {
            'total': result['total'] or 0,
            'count': result['count'] or 0,
        }

    def sales_last_7_days(self):
        """Daily sales for the last 7 days (for chart)."""
        today = timezone.now().date()
        days = []
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            qs = self._base_orders().filter(date__date=d)
            agg = qs.aggregate(total=Sum('total_clp'), count=Count('id'))
            days.append({
                'date': d,
                'label': d.strftime('%a %d'),
                'total': agg['total'] or 0,
                'count': agg['count'] or 0,
            })
        return days

    def sales_by_payment_method(self):
        """Breakdown by payment method (for pie chart)."""
        qs = Payment.all_objects.filter(
            order__tenant=self.tenant,
            order__is_paid=True,
            order__is_voided=False,
            order__date__date=timezone.now().date(),
        )
        return list(qs.values('method').annotate(
            total=Sum('amount_clp'), count=Count('id'),
        ).order_by('-total'))

    # ──────────── Product metrics ────────────

    def top_products(self, limit=10, days=30):
        """Top products by revenue in the last N days."""
        cutoff = timezone.now() - timedelta(days=days)
        return list(OrderItem.objects.filter(
            order__tenant=self.tenant,
            order__is_paid=True,
            order__is_voided=False,
            order__date__gte=cutoff,
        ).values(
            'product__name', 'product__sku',
        ).annotate(
            total_sold=Sum('quantity'),
            total_revenue=Sum('line_total_clp'),
        ).order_by('-total_revenue')[:limit])

    # ──────────── Inventory alerts ────────────

    def low_stock_alerts(self):
        """Products below their minimum stock threshold."""
        return Product.all_objects.filter(
            tenant=self.tenant,
            stock__lte=F('min_stock_alert'),
        ).order_by('stock')

    def expiration_alerts(self, days=30):
        """Batches expiring within N days."""
        cutoff = date.today() + timedelta(days=days)
        return Batch.all_objects.filter(
            tenant=self.tenant,
            expiration_date__lte=cutoff,
            current_quantity__gt=0,
        ).select_related('product').order_by('expiration_date')

    def expired_batches(self):
        """Batches already expired with remaining stock."""
        return Batch.all_objects.filter(
            tenant=self.tenant,
            expiration_date__lt=date.today(),
            current_quantity__gt=0,
        ).select_related('product').order_by('expiration_date')

    # ──────────── Margin report ────────────

    def margin_report(self, days=30):
        """Revenue vs cost by product."""
        cutoff = timezone.now() - timedelta(days=days)
        items = list(OrderItem.objects.filter(
            order__tenant=self.tenant,
            order__is_paid=True,
            order__is_voided=False,
            order__date__gte=cutoff,
        ).values('product__name', 'product__sku').annotate(
            revenue=Sum('line_total_clp'),
            cost=Sum(F('cost_at_sale') * F('quantity')),
            qty=Sum('quantity'),
        ).order_by('-revenue'))

        for item in items:
            cost = item['cost'] or 0
            revenue = item['revenue'] or 0
            item['margin'] = revenue - cost
            item['margin_pct'] = (
                round(((revenue - cost) / cost) * 100, 1) if cost > 0 else 0
            )
        return items

    # ──────────── Summary dict (for dashboard) ────────────

    def dashboard_summary(self):
        """Returns all KPIs for the main dashboard view."""
        return {
            'today': self.sales_today(),
            'week': self.sales_this_week(),
            'month': self.sales_this_month(),
            'last_7_days': self.sales_last_7_days(),
            'payment_methods': self.sales_by_payment_method(),
            'top_products': self.top_products(limit=5),
            'low_stock': list(self.low_stock_alerts()[:10]),
            'expiring': list(self.expiration_alerts(days=30)[:10]),
            'expired': list(self.expired_batches()[:5]),
        }
