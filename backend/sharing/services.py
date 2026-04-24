"""Sharing services."""
from django.contrib.auth.hashers import check_password, make_password
from django.db.models import Count
from django.utils import timezone

from cases.models import Case
from products.models import Product
from products.serializers import ProductDetailSerializer, ProductListSerializer
from cases.serializers import CaseDetailSerializer
from quotes.models import Quote
from quotes.serializers import QuoteDetailSerializer
from .models import ClickTrackingLog, ShareAccessLog, ShareLink


class ShareService:
    @staticmethod
    def create_link(data: dict, user) -> ShareLink:
        password = data.pop('password', None)
        link = ShareLink(created_by=user, **data)
        if password:
            link.password_hash = make_password(password)
        link.save()
        return link

    @staticmethod
    def validate_access(share: ShareLink) -> str | None:
        if not share.is_active:
            return '链接已失效'
        if share.expires_at and timezone.now() > share.expires_at:
            return '链接已过期'
        if share.max_access_count and share.access_count >= share.max_access_count:
            return '链接已失效'
        return None

    @staticmethod
    def verify_password(share: ShareLink, password: str) -> bool:
        if not share.password_hash:
            return True
        return check_password(password, share.password_hash)

    @staticmethod
    def log_access(share: ShareLink, request):
        share.access_count += 1
        share.save(update_fields=['access_count'])
        ShareAccessLog.objects.create(
            share_link=share,
            ip_address=request.META.get('REMOTE_ADDR', ''),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
        )

    @staticmethod
    def get_shared_content(share: ShareLink) -> dict:
        if share.content_type == 'PRODUCT':
            obj = Product.objects.prefetch_related('images', 'configs').get(pk=share.object_id)
            return {'type': 'product', 'data': ProductDetailSerializer(obj).data}
        elif share.content_type == 'CASE':
            obj = Case.objects.prefetch_related('images', 'products').get(pk=share.object_id)
            return {'type': 'case', 'data': CaseDetailSerializer(obj).data}
        elif share.content_type == 'QUOTE':
            obj = Quote.objects.prefetch_related('items').get(pk=share.object_id)
            return {'type': 'quote', 'data': QuoteDetailSerializer(obj).data}
        elif share.content_type == 'CATALOG':
            products = Product.objects.filter(is_active=True).prefetch_related('images')[:50]
            return {'type': 'catalog', 'data': ProductListSerializer(products, many=True).data}
        return {}

    @staticmethod
    def track_click(share: ShareLink, data: dict, request):
        ClickTrackingLog.objects.create(
            share_link=share,
            event_type=data.get('event_type', ''),
            object_id=data.get('object_id', 0),
            object_name=data.get('object_name', ''),
            ip_address=request.META.get('REMOTE_ADDR', ''),
        )

    @staticmethod
    def get_click_stats(share: ShareLink) -> list:
        return list(
            share.click_logs.values('event_type', 'object_id', 'object_name')
            .annotate(click_count=Count('id'))
            .order_by('-click_count')
        )
