from django.urls import path

from .views import ChatView, LandingView

app_name = 'landing'

urlpatterns = [
    path('', LandingView.as_view(), name='home'),
    path('chat/', ChatView.as_view(), name='chat'),
]
