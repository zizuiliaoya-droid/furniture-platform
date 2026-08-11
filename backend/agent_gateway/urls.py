from django.urls import path

from .views import AgentCapabilitiesView


urlpatterns = [
    path('capabilities/', AgentCapabilitiesView.as_view(), name='agent-capabilities'),
]
