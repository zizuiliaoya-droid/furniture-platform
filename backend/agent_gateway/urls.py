from django.urls import path

from .views import (
    AgentCapabilitiesView,
    AgentCaseSearchView,
    AgentDocumentSearchView,
    AgentConfigImportConfirmView,
    AgentConfigImportPreviewView,
    AgentPriceCalculationView,
    AgentProductDetailView,
    AgentProductSearchView,
    AgentQuoteDraftView,
)


urlpatterns = [
    path('capabilities/', AgentCapabilitiesView.as_view(), name='agent-capabilities'),
    path('products/search/', AgentProductSearchView.as_view(), name='agent-product-search'),
    path('products/<int:product_id>/', AgentProductDetailView.as_view(), name='agent-product-detail'),
    path('products/<int:product_id>/price/', AgentPriceCalculationView.as_view(), name='agent-price'),
    path('products/<int:product_id>/config-import/preview/', AgentConfigImportPreviewView.as_view(), name='agent-config-import-preview'),
    path('products/<int:product_id>/config-import/confirm/', AgentConfigImportConfirmView.as_view(), name='agent-config-import-confirm'),
    path('documents/search/', AgentDocumentSearchView.as_view(), name='agent-document-search'),
    path('cases/search/', AgentCaseSearchView.as_view(), name='agent-case-search'),
    path('quotes/drafts/', AgentQuoteDraftView.as_view(), name='agent-quote-draft'),
]
