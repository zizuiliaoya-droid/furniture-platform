"""Narrow, auditable endpoints exposed to agent clients."""
from io import BytesIO
from time import perf_counter
import json
import re

from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cases.models import Case
from documents.models import Document
from products.models import Product
from products.serializers import CalculatePriceSerializer
from products.services import FlexibleConfigExcelService, PriceCalculationService
from quotes.models import Quote
from quotes.serializers import QuoteDetailSerializer
from quotes.services import QuoteService

from .models import AgentActionAudit
from .serializers import (
    AgentContentSearchQuerySerializer,
    AgentProductDetailSerializer,
    AgentProductSearchQuerySerializer,
    AgentProductSummarySerializer,
    AgentQuoteDraftSerializer,
)
from .services import (
    ConfirmationInvalid,
    ConfirmationReplay,
    IdempotencyConflict,
    IdempotencyInProgress,
    agent_request_id,
    consume_confirmation,
    import_request_digest,
    issue_confirmation,
    public_web_url,
    record_agent_audit,
    require_agent_permission,
    run_idempotent,
    verify_confirmation,
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


def _failure_response(
    request, request_id, started_at, action, detail, input_data,
    *, status_code=status.HTTP_400_BAD_REQUEST,
):
    record_agent_audit(
        request=request,
        request_id=request_id,
        action=action,
        status=AgentActionAudit.Status.FAILED,
        started_at=started_at,
        input_data=input_data,
        output_data={'detail': str(detail)},
    )
    return _agent_response(
        {'request_id': request_id, 'detail': str(detail)},
        request_id,
        status_code=status_code,
    )


def _parse_bool(value, default=False):
    if value is None or value == '':
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().casefold() in {'true', '1', 'yes', 'y', '是'}


def _parse_mapping(raw):
    if raw in (None, ''):
        return {}
    if isinstance(raw, dict):
        return raw
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise ValueError('mapping 必须是 JSON 对象')
    return parsed


def _read_excel_upload(request):
    uploaded = request.FILES.get('file')
    if not uploaded:
        raise ValueError('请上传 .xlsx 文件')
    if not uploaded.name.lower().endswith('.xlsx'):
        raise ValueError('仅支持 .xlsx 文件')
    if uploaded.size > settings.AGENT_MAX_IMPORT_SIZE:
        raise ValueError('Excel 文件超过 Agent 导入大小限制')
    content = uploaded.read()
    uploaded.seek(0)
    if not content:
        raise ValueError('Excel 文件为空')
    return uploaded.name, content


def _import_preview_payload(parsed):
    return {
        'pricing_mode': parsed['pricing_mode'],
        'base_price': str(parsed['base_price']) if parsed['base_price'] is not None else None,
        'dimensions_count': len(parsed['dimensions']),
        'dimensions': parsed['dimensions'],
        'price_entries_count': parsed['success_count'],
        'preset_count': len(parsed.get('presets', [])),
        'failed_count': parsed['failed_count'],
        'detected_format': parsed.get('detected_format'),
        'needs_mapping': parsed.get('needs_mapping', False),
        'available_sheets': parsed.get('available_sheets', []),
        'impact': parsed.get('impact', {}),
        'errors': parsed['errors'],
        'warnings': parsed.get('warnings', []),
    }


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


class AgentQuoteDraftView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        started_at = perf_counter()
        request_id = agent_request_id(request)
        action = 'quote.create_draft'
        require_agent_permission(
            request=request, request_id=request_id, started_at=started_at,
            action=action, module='QUOTE', permission='create',
            input_data=request.data,
        )
        idempotency_key = str(request.headers.get('Idempotency-Key') or '').strip()
        if not (
            8 <= len(idempotency_key) <= 128
            and re.fullmatch(r'[A-Za-z0-9_.:-]+', idempotency_key)
        ):
            return _failure_response(
                request, request_id, started_at, action,
                '必须提供 8-128 位 Idempotency-Key（字母、数字、点、冒号、短横线或下划线）',
                request.data,
            )
        serializer = AgentQuoteDraftSerializer(data=request.data)
        if not serializer.is_valid():
            return _invalid_response(
                request, request_id, started_at, action,
                serializer.errors, request.data,
            )
        validated = serializer.validated_data

        def create_draft():
            quote = Quote.objects.create(
                title=validated['title'],
                customer_name=validated['customer_name'],
                status='DRAFT',
                notes=validated.get('notes', ''),
                terms=validated.get('terms', ''),
                discount=validated.get('discount', 0),
                created_by=request.user,
            )
            for item_data in validated['items']:
                product = Product.objects.filter(
                    pk=item_data['product_id'],
                    is_active=True,
                ).first()
                if not product:
                    raise DRFValidationError({
                        'items': f'产品 {item_data["product_id"]} 不存在或已下架',
                    })
                QuoteService.add_item_from_product(
                    quote,
                    product,
                    item_data.get('selections', {}),
                    image_id=item_data.get('image_id'),
                    quantity=item_data.get('quantity', 1),
                )
            quote.refresh_from_db()
            response_data = {
                'quote': QuoteDetailSerializer(quote).data,
                'web_url': f'{public_web_url()}/quotes/{quote.id}',
            }
            return response_data, 'Quote', quote.id

        try:
            result, replayed = run_idempotent(
                user=request.user,
                action=action,
                key=idempotency_key,
                payload=validated,
                operation=create_draft,
            )
        except DRFValidationError as exc:
            return _invalid_response(
                request, request_id, started_at, action,
                exc.detail, validated,
            )
        except (IdempotencyConflict, IdempotencyInProgress) as exc:
            return _failure_response(
                request, request_id, started_at, action, exc, validated,
                status_code=status.HTTP_409_CONFLICT,
            )
        payload = {'request_id': request_id, 'replayed': replayed, **result}
        record_agent_audit(
            request=request, request_id=request_id, action=action,
            status=AgentActionAudit.Status.SUCCEEDED, started_at=started_at,
            input_data={'idempotency_key': idempotency_key, **validated},
            output_data={
                'quote_id': result['quote']['id'],
                'replayed': replayed,
            },
            object_type='Quote', object_id=result['quote']['id'],
        )
        return _agent_response(
            payload,
            request_id,
            status_code=(status.HTTP_200_OK if replayed else status.HTTP_201_CREATED),
        )


class AgentConfigImportPreviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        started_at = perf_counter()
        request_id = agent_request_id(request)
        action = 'product.config_import_preview'
        input_summary = {'product_id': product_id, 'file_name': ''}
        require_agent_permission(
            request=request, request_id=request_id, started_at=started_at,
            action=action, module='PRODUCT', permission='update',
            input_data=input_summary,
        )
        product = get_object_or_404(Product, pk=product_id)
        try:
            file_name, content = _read_excel_upload(request)
            mapping = _parse_mapping(request.data.get('mapping'))
            replace_dimensions = _parse_bool(request.data.get('replace_dimensions'), False)
            replace_prices = _parse_bool(request.data.get('replace_prices'), True)
            input_summary.update({
                'file_name': file_name,
                'file_size': len(content),
                'mapping': mapping,
                'replace_dimensions': replace_dimensions,
                'replace_prices': replace_prices,
            })
            parsed = FlexibleConfigExcelService.parse_excel(
                product,
                BytesIO(content),
                mapping=mapping,
            )
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            return _failure_response(
                request, request_id, started_at, action, exc, input_summary,
            )
        digest = import_request_digest(
            content,
            product_id=product_id,
            mapping=mapping,
            replace_dimensions=replace_dimensions,
            replace_prices=replace_prices,
        )
        can_confirm = not parsed.get('errors') and not parsed.get('needs_mapping')
        confirmation_token = ''
        if can_confirm:
            confirmation_token = issue_confirmation(
                user=request.user,
                action='product.config_import_confirm',
                resource_id=product_id,
                request_digest=digest,
            )
        preview = _import_preview_payload(parsed)
        payload = {
            'request_id': request_id,
            'preview': preview,
            'can_confirm': can_confirm,
            'confirmation_token': confirmation_token,
            'confirmation_expires_in': settings.AGENT_CONFIRMATION_MAX_AGE,
        }
        record_agent_audit(
            request=request, request_id=request_id, action=action,
            status=AgentActionAudit.Status.SUCCEEDED, started_at=started_at,
            input_data=input_summary,
            output_data={
                'can_confirm': can_confirm,
                'dimensions_count': preview['dimensions_count'],
                'price_entries_count': preview['price_entries_count'],
                'failed_count': preview['failed_count'],
            },
            object_type='Product', object_id=product_id,
        )
        return _agent_response(payload, request_id)


class AgentConfigImportConfirmView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        started_at = perf_counter()
        request_id = agent_request_id(request)
        action = 'product.config_import_confirm'
        input_summary = {'product_id': product_id, 'file_name': ''}
        require_agent_permission(
            request=request, request_id=request_id, started_at=started_at,
            action=action, module='PRODUCT', permission='update',
            input_data=input_summary,
        )
        product = get_object_or_404(Product, pk=product_id)
        token = str(request.data.get('confirmation_token') or '').strip()
        if not token:
            return _failure_response(
                request, request_id, started_at, action,
                '缺少确认票据，请先调用预览接口', input_summary,
            )
        try:
            file_name, content = _read_excel_upload(request)
            mapping = _parse_mapping(request.data.get('mapping'))
            replace_dimensions = _parse_bool(request.data.get('replace_dimensions'), False)
            replace_prices = _parse_bool(request.data.get('replace_prices'), True)
            input_summary.update({
                'file_name': file_name,
                'file_size': len(content),
                'mapping': mapping,
                'replace_dimensions': replace_dimensions,
                'replace_prices': replace_prices,
                'confirmation_token': token,
            })
            digest = import_request_digest(
                content,
                product_id=product_id,
                mapping=mapping,
                replace_dimensions=replace_dimensions,
                replace_prices=replace_prices,
            )
            verify_confirmation(
                token=token,
                user=request.user,
                action=action,
                resource_id=product_id,
                request_digest=digest,
            )
            parsed = FlexibleConfigExcelService.parse_excel(
                product,
                BytesIO(content),
                mapping=mapping,
            )
            if parsed.get('errors') or parsed.get('needs_mapping'):
                raise ValueError('文件重新解析后仍有错误或未完成映射，禁止导入')
            with transaction.atomic():
                consume_confirmation(
                    token=token,
                    user=request.user,
                    action=action,
                    resource_id=product_id,
                    request_id=request_id,
                )
                result = FlexibleConfigExcelService.execute_import(
                    product,
                    parsed,
                    replace_dimensions=replace_dimensions,
                    replace_prices=replace_prices,
                )
        except ConfirmationReplay as exc:
            return _failure_response(
                request, request_id, started_at, action, exc, input_summary,
                status_code=status.HTTP_409_CONFLICT,
            )
        except (ConfirmationInvalid, ValueError, TypeError, json.JSONDecodeError) as exc:
            return _failure_response(
                request, request_id, started_at, action, exc, input_summary,
            )
        payload = {
            'request_id': request_id,
            'detail': '导入成功',
            'result': result,
            'product_url': f'{public_web_url()}/products/{product_id}/edit',
        }
        record_agent_audit(
            request=request, request_id=request_id, action=action,
            status=AgentActionAudit.Status.SUCCEEDED, started_at=started_at,
            input_data=input_summary,
            output_data=result,
            object_type='Product', object_id=product_id,
        )
        return _agent_response(payload, request_id)
