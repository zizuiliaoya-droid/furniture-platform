"""Global search view."""
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from cases.models import Case
from documents.models import Document
from products.models import Product
from quotes.models import Quote


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def global_search_view(request):
    q = request.query_params.get('q', '').strip()
    if len(q) < 2:
        return Response({'products': [], 'cases': [], 'documents': [], 'quotes': []})

    product_qs = Product.objects.filter(is_active=True).filter(
        Q(name__icontains=q) | Q(code__icontains=q)
    )[:5]
    case_qs = Case.objects.filter(title__icontains=q)[:5]
    doc_qs = Document.objects.filter(name__icontains=q)[:5]
    quote_qs = Quote.objects.filter(
        Q(title__icontains=q) | Q(customer_name__icontains=q)
    )[:5]

    return Response({
        'products': [{'id': p.id, 'name': p.name, 'code': p.code} for p in product_qs],
        'cases': [{'id': c.id, 'title': c.title, 'industry': c.industry} for c in case_qs],
        'documents': [{'id': d.id, 'name': d.name, 'doc_type': d.doc_type} for d in doc_qs],
        'quotes': [{'id': q_.id, 'title': q_.title, 'customer_name': q_.customer_name} for q_ in quote_qs],
    })
