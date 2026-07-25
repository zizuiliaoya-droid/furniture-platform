"""Dashboard services."""
from datetime import timedelta

from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.utils import timezone

from auth_app.permissions import has_module_permission
from cases.models import Case
from documents.models import Document
from products.models import Product
from quotes.models import Quote


class DashboardService:
    @staticmethod
    def get_stats(user) -> dict:
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        thirty_days_ago = now - timedelta(days=30)

        products = (Product.objects.filter(is_active=True)
                    if has_module_permission(user, 'PRODUCT', 'view') else Product.objects.none())
        cases = Case.objects.all() if has_module_permission(user, 'CASE', 'view') else Case.objects.none()
        documents = (Document.objects.all()
                     if has_module_permission(user, 'DOCUMENT', 'view') else Document.objects.none())
        quotes = Quote.objects.all() if has_module_permission(user, 'QUOTE', 'view') else Quote.objects.none()
        if not getattr(user, 'is_admin', False):
            quotes = quotes.filter(Q(created_by=user) | Q(shares__shared_with=user)).distinct()

        totals = {
            'product_count': products.count(),
            'case_count': cases.count(),
            'quote_count': quotes.count(),
            'document_count': documents.count(),
        }
        monthly = {
            'new_products': products.filter(created_at__gte=month_start).count(),
            'new_cases': cases.filter(created_at__gte=month_start).count(),
            'new_quotes': quotes.filter(created_at__gte=month_start).count(),
        }
        daily_products = dict(
            products.filter(created_at__gte=thirty_days_ago)
            .annotate(date=TruncDate('created_at')).values('date')
            .annotate(count=Count('id')).values_list('date', 'count')
        )
        daily_cases = dict(
            cases.filter(created_at__gte=thirty_days_ago)
            .annotate(date=TruncDate('created_at')).values('date')
            .annotate(count=Count('id')).values_list('date', 'count')
        )
        daily_quotes = dict(
            quotes.filter(created_at__gte=thirty_days_ago)
            .annotate(date=TruncDate('created_at')).values('date')
            .annotate(count=Count('id')).values_list('date', 'count')
        )
        daily = []
        for i in range(30):
            date = (now - timedelta(days=29 - i)).date()
            daily.append({
                'date': date.isoformat(),
                'products': daily_products.get(date, 0),
                'cases': daily_cases.get(date, 0),
                'quotes': daily_quotes.get(date, 0),
            })

        recent_quotes = quotes.select_related('created_by').order_by('-updated_at')[:10]
        recent_activities = [
            {
                'id': quote.id, 'title': quote.title,
                'customer_name': quote.customer_name,
                'status': quote.status,
                'updated_at': quote.updated_at.isoformat(),
            }
            for quote in recent_quotes
        ]

        return {
            'totals': totals,
            'monthly': monthly,
            'daily': daily,
            'recent_activities': recent_activities,
        }
