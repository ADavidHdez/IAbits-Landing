from django.urls import path

from . import content
from .views import LegalPageView

app_name = 'legal'

urlpatterns = [
    path('aviso-legal/', LegalPageView.as_view(page=content.LEGAL_NOTICE), name='notice'),
    path('privacidad/', LegalPageView.as_view(page=content.PRIVACY), name='privacy'),
    path('cookies/', LegalPageView.as_view(page=content.COOKIES), name='cookies'),
]
