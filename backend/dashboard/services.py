"""Dashboard services."""
from datetime import timedelta
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone

from cases.models import Case
from documents.models import Document
from products.models import Product
from quotes.models import Quote


class DashboardService:
    @staticmethod
    def get_stats() -> dict:
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        thirty_days_ago = now - timedelta(days=30)

        totals = {
            'product_count': Product.objects.filter(is_active=True).count(),
            'case_count': Case.objects.count(),
            'quote_count': Quote.objects.count(),
            'document_count': Document.objects.count(),
        }
        monthly = {
            'new_products': Product.objects.filter(created_at__gte=month_start, is_active=True).count(),
            'new_cases': Case.objects.filter(created_at__gte=month_start).count(),
            'new_quotes': Quote.objects.filter(created_at__gte=month_start).count(),
        }
        daily_products = dict(
            Product.objects.filter(created_at__gte=thirty_days_ago, is_active=True)
            .annotate(date=TruncDate('created_at')).values('date')
            .annotate(count=Count('id')).values_list('date', 'count')
        )
        daily_cases = dict(
            Case.objects.filter(created_at__gte=thirty_days_ago)
            .annotate(date=TruncDate('created_at')).values('date')
            .annotate(count=Count('id')).values_list('date', 'count')
        )
        daily_quotes = dict(
            Quote.objects.filter(created_at__gte=thirty_days_ago)
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

        recent_quotes = Quote.objects.select_related('created_by').order_by('-updated_at')[:10]
        recent_activities = [
            {
                'id': q.id, 'title': q.title,
                'customer_name': q.customer_name,
                'status': q.status,
                'updated_at': q.updated_at.isoformat(),
            }
            for q in recent_quotes
        ]

        return {
            'totals': totals,
            'monthly': monthly,
            'daily': daily,
            'recent_activities': recent_activities,
        }
