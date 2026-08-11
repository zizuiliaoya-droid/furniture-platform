"""Narrow, auditable endpoints exposed to agent clients."""
from time import perf_counter

from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cases.models import Case
from documents.models import Document
from products.models import Product
from products.serializers import CalculatePriceSerializer
from products.services import PriceCalculationService

from .models import AgentActionAudit
from .serializers import (
    AgentContentSearchQuerySerializer,
    AgentProductDetailSerializer,
    AgentProductSearchQuerySerializer,
    AgentProductSummarySerializer,
)
from .services import (
    agent_request_id,
    public_web_url,
    record_agent_audit,
    require_agent_permission,
    visible_capabilities,
)


def _agent_response(payload, request_id, *, status_code=status.HTTP_200_OK):
    response = Response(payload, status=status_code)
    response['X-Request-ID'] = request_id
    return response


def _invalid_response(request, request_id, started_at, action, errors, input_data):
    record_agent_audit(
        request=request,
        request_id=request_id,
        action=action,
        status=AgentActionAudit.Status.FAILED,
        started_at=started_at,
        input_data=input_data,
        output_data={'errors': errors},
    )
    return _agent_response(
        {'request_id': request_id, 'errors': errors},
        request_id,
        status_code=status.HTTP_400_BAD_REQUEST,
    )


class AgentCapabilitiesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        started_at = perf_counter()
        request_id = agent_request_id(request)
        payload = {
            'schema_version': '1.0',
            'request_id': request_id,
            'web_url': public_web_url(),
            'capabilities': visible_capabilities(request.user),
        }
        record_agent_audit(
            request=request,
            request_id=request_id,
            action='system.capabilities',
            status=AgentActionAudit.Status.SUCCEEDED,
            started_at=started_at,
            input_data={'method': request.method, 'path': request.path},
            output_data={'capability_count': len(payload['capabilities'])},
        )
        response = Response(payload)
        response['X-Request-ID'] = request_id
        return response


class AgentProductSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        started_at = perf_counter()
        request_id = agent_request_id(request)
        action = 'catalog.search'
        require_agent_permission(
            request=request, request_id=request_id, started_at=started_at,
            action=action, module='CATALOG', permission='view',
            input_data=request.query_params.dict(),
        )
        query = AgentProductSearchQuerySerializer(data=request.query_params)
        if not query.is_valid():
            return _invalid_response(
                request, request_id, started_at, action,
                query.errors, request.query_params.dict(),
            )
        params = query.validated_data
        products = Product.objects.filter(is_active=True).select_related('brand').prefetch_related('images')
        keyword = params.get('q', '').strip()
        if keyword:
            products = products.filter(
                Q(name__icontains=keyword)
                | Q(code__icontains=keyword)
                | Q(description__icontains=keyword)
                | Q(config_dimensions__dimension_label__icontains=keyword)
                | Q(config_dimensions__options__icontains=keyword)
            )
        for field in ('category_l1', 'category_l2', 'origin', 'lead_time'):
            if params.get(field):
                products = products.filter(**{field: params[field]})
        if params.get('brand'):
            products = products.filter(brand_id=params['brand'])
        if params.get('min_price') is not None:
            products = products.filter(min_price__gte=params['min_price'])
        if params.get('max_price') is not None:
            products = products.filter(min_price__lte=params['max_price'])
        products = products.distinct().order_by('-created_at')
        count = products.count()
        page, page_size = params['page'], params['page_size']
        offset = (page - 1) * page_size
        items = AgentProductSummarySerializer(
            products[offset:offset + page_size],
            many=True,
            context={'web_url': public_web_url()},
        ).data
        payload = {
            'request_id': request_id,
            'count': count,
            'page': page,
            'page_size': page_size,
            'items': items,
        }
        record_agent_audit(
            request=request, request_id=request_id, action=action,
            status=AgentActionAudit.Status.SUCCEEDED, started_at=started_at,
            input_data=params, output_data={'count': count, 'returned': len(items)},
        )
        return _agent_response(payload, request_id)


class AgentProductDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, product_id):
        started_at = perf_counter()
        request_id = agent_request_id(request)
        action = 'product.detail'
        require_agent_permission(
            request=request, request_id=request_id, started_at=started_at,
            action=action, module='PRODUCT', permission='view',
            input_data={'product_id': product_id},
        )
        products = Product.objects.select_related('brand').prefetch_related(
            'images', 'config_dimensions', 'config_presets',
        )
        if not request.user.is_admin:
            products = products.filter(is_active=True)
        product = get_object_or_404(products, pk=product_id)
        item = AgentProductDetailSerializer(
            product,
            context={'web_url': public_web_url()},
        ).data
        payload = {'request_id': request_id, 'item': item}
        record_agent_audit(
            request=request, request_id=request_id, action=action,
            status=AgentActionAudit.Status.SUCCEEDED, started_at=started_at,
            input_data={'product_id': product_id},
            output_data={'product_id': product_id},
            object_type='Product', object_id=product_id,
        )
        return _agent_response(payload, request_id)


class AgentPriceCalculationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        started_at = perf_counter()
        request_id = agent_request_id(request)
        action = 'product.calculate_price'
        require_agent_permission(
            request=request, request_id=request_id, started_at=started_at,
            action=action, module='PRODUCT', permission='view',
            input_data={'product_id': product_id, **request.data},
        )
        products = Product.objects.prefetch_related(
            'config_dimensions', 'price_matrix', 'price_rules',
        )
        if not request.user.is_admin:
            products = products.filter(is_active=True)
        product = get_object_or_404(products, pk=product_id)
        serializer = CalculatePriceSerializer(data=request.data)
        if not serializer.is_valid():
            return _invalid_response(
                request, request_id, started_at, action,
                serializer.errors, {'product_id': product_id, **request.data},
            )
        result = PriceCalculationService.calculate(
            product,
            serializer.validated_data['selections'],
        )
        payload = {
            'request_id': request_id,
            'product_id': product_id,
            'source': 'PriceCalculationService',
            **result,
        }
        record_agent_audit(
            request=request, request_id=request_id, action=action,
            status=AgentActionAudit.Status.SUCCEEDED, started_at=started_at,
            input_data={'product_id': product_id, **serializer.validated_data},
            output_data={'valid': result['valid'], 'price': result.get('price')},
            object_type='Product', object_id=product_id,
        )
        return _agent_response(payload, request_id)


DOCUMENT_PATHS = {
    'DESIGN': 'design',
    'TRAINING': 'training',
    'CERTIFICATE': 'certificates',
}


class AgentDocumentSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        started_at = perf_counter()
        request_id = agent_request_id(request)
        action = 'document.search'
        require_agent_permission(
            request=request, request_id=request_id, started_at=started_at,
            action=action, module='DOCUMENT', permission='view',
            input_data=request.query_params.dict(),
        )
        query = AgentContentSearchQuerySerializer(data=request.query_params)
        if not query.is_valid():
            return _invalid_response(
                request, request_id, started_at, action,
                query.errors, request.query_params.dict(),
            )
        params = query.validated_data
        documents = Document.objects.select_related('folder').all()
        keyword = params.get('q', '').strip()
        if keyword:
            documents = documents.filter(
                Q(name__icontains=keyword) | Q(content__icontains=keyword)
            )
        if params.get('doc_type'):
            documents = documents.filter(doc_type=params['doc_type'])
        count = documents.count()
        items = []
        for document in documents[:params['limit']]:
            excerpt = document.content[:500]
            if len(document.content) > 500:
                excerpt += '…'
            items.append({
                'id': document.id,
                'name': document.name,
                'doc_type': document.doc_type,
                'resource_type': document.resource_type,
                'folder': document.folder.name if document.folder else '',
                'tags': document.tags,
                'content_excerpt': excerpt,
                'file_path': document.file_path,
                'web_url': (
                    f'{public_web_url()}/documents/'
                    f'{DOCUMENT_PATHS.get(document.doc_type, "design")}'
                ),
            })
        payload = {'request_id': request_id, 'count': count, 'items': items}
        record_agent_audit(
            request=request, request_id=request_id, action=action,
            status=AgentActionAudit.Status.SUCCEEDED, started_at=started_at,
            input_data=params, output_data={'count': count, 'returned': len(items)},
        )
        return _agent_response(payload, request_id)


class AgentCaseSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        started_at = perf_counter()
        request_id = agent_request_id(request)
        action = 'case.search'
        require_agent_permission(
            request=request, request_id=request_id, started_at=started_at,
            action=action, module='CASE', permission='view',
            input_data=request.query_params.dict(),
        )
        query = AgentContentSearchQuerySerializer(data=request.query_params)
        if not query.is_valid():
            return _invalid_response(
                request, request_id, started_at, action,
                query.errors, request.query_params.dict(),
            )
        params = query.validated_data
        cases = Case.objects.prefetch_related('products').all()
        keyword = params.get('q', '').strip()
        if keyword:
            cases = cases.filter(
                Q(title__icontains=keyword) | Q(description__icontains=keyword)
            )
        if params.get('industry'):
            cases = cases.filter(industry=params['industry'])
        count = cases.count()
        items = [{
            'id': item.id,
            'title': item.title,
            'description_excerpt': (
                item.description[:500] + ('…' if len(item.description) > 500 else '')
            ),
            'industry': item.industry,
            'related_product_ids': [product.id for product in item.products.all()],
            'web_url': f'{public_web_url()}/cases/{item.id}',
        } for item in cases[:params['limit']]]
        payload = {'request_id': request_id, 'count': count, 'items': items}
        record_agent_audit(
            request=request, request_id=request_id, action=action,
            status=AgentActionAudit.Status.SUCCEEDED, started_at=started_at,
            input_data=params, output_data={'count': count, 'returned': len(items)},
        )
        return _agent_response(payload, request_id)
