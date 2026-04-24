"""Quote models."""
from decimal import Decimal
from django.conf import settings
from django.db import models


class Quote(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', '草稿'),
        ('SENT', '已发送'),
        ('CONFIRMED', '已确认'),
        ('CANCELLED', '已取消'),
    ]
    title = models.CharField(max_length=200)
    customer_name = models.CharField(max_length=200)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='DRAFT')
    notes = models.TextField(blank=True, default='')
    terms = models.TextField(blank=True, default='')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['-updated_at']),
        ]

    def recalculate_total(self):
        total = self.items.aggregate(total=models.Sum('subtotal'))['total'] or Decimal('0')
        self.total_amount = total
        self.save(update_fields=['total_amount'])

    def __str__(self):
        return f"{self.title} - {self.customer_name}"


class QuoteItem(models.Model):
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', null=True, blank=True, on_delete=models.SET_NULL)
    product_name = models.CharField(max_length=200)
    config_name = models.CharField(max_length=200, blank=True, default='')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0'))
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'id']

    def save(self, *args, **kwargs):
        self.subtotal = self.unit_price * self.quantity * (1 - self.discount / 100)
        super().save(*args, **kwargs)
