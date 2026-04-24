"""Quote services."""
from django.db import transaction
from django.template.loader import render_to_string

try:
    from weasyprint import HTML
    HAS_WEASYPRINT = True
except (ImportError, OSError):
    HAS_WEASYPRINT = False

from .models import Quote, QuoteItem

VALID_TRANSITIONS = {
    'DRAFT': ['SENT', 'CANCELLED'],
    'SENT': ['CONFIRMED', 'CANCELLED'],
    'CONFIRMED': ['CANCELLED'],
    'CANCELLED': [],
}


class QuoteService:
    @staticmethod
    def validate_status_change(current: str, new_status: str) -> bool:
        return new_status in VALID_TRANSITIONS.get(current, [])

    @staticmethod
    @transaction.atomic
    def duplicate(quote_id: int, user) -> Quote:
        original = Quote.objects.prefetch_related('items').get(pk=quote_id)
        new_quote = Quote.objects.create(
            title=f"{original.title}(副本)",
            customer_name=original.customer_name,
            status='DRAFT',
            notes=original.notes,
            terms=original.terms,
            created_by=user,
        )
        for item in original.items.all():
            QuoteItem.objects.create(
                quote=new_quote,
                product=item.product,
                product_name=item.product_name,
                config_name=item.config_name,
                unit_price=item.unit_price,
                quantity=item.quantity,
                discount=item.discount,
                sort_order=item.sort_order,
            )
        new_quote.recalculate_total()
        return new_quote

    @staticmethod
    def export_pdf(quote_id: int) -> bytes:
        if not HAS_WEASYPRINT:
            raise ImportError('WeasyPrint is not installed. Install it with: pip install WeasyPrint')
        quote = Quote.objects.prefetch_related('items').get(pk=quote_id)
        html_string = render_to_string('quotes/pdf_template.html', {'quote': quote})
        pdf = HTML(string=html_string).write_pdf()
        return pdf
