from django.urls import path

from .views import (
    AgentCapabilitiesView,
    AgentCaseSearchView,
    AgentDocumentSearchView,
    AgentPriceCalculationView,
    AgentProductDetailView,
    AgentProductSearchView,
)


urlpatterns = [
    path('capabilities/', AgentCapabilitiesView.as_view(), name='agent-capabilities'),
    path('products/search/', AgentProductSearchView.as_view(), name='agent-product-search'),
    path('products/<int:product_id>/', AgentProductDetailView.as_view(), name='agent-product-detail'),
    path('products/<int:product_id>/price/', AgentPriceCalculationView.as_view(), name='agent-price'),
    path('documents/search/', AgentDocumentSearchView.as_view(), name='agent-document-search'),
    path('cases/search/', AgentCaseSearchView.as_view(), name='agent-case-search'),
]
