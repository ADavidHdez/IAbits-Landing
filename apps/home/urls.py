from django.urls import path

from .views import ContactView, HomeView

app_name = 'home'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('contacto/', ContactView.as_view(), name='contact'),
]
