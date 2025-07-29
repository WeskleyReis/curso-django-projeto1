from django.urls import path
from .views import home, contato, sobre

app_name = 'recipes'

urlpatterns = [
    path('', home, name='home'),
    path('contato/', contato, name='contato'),
    path('sobre/', sobre, name='sobre'),
]
