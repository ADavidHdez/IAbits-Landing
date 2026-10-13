from django.urls import path

from .views import LandingView

app_name = 'landing'

# El endpoint del chat (ChatView) no cuelga de aquí sino de /chat/ en
# config/urls.py: lo usan la landing y la home, que no se enlazan entre sí.
urlpatterns = [
    path('', LandingView.as_view(), name='home'),
]
