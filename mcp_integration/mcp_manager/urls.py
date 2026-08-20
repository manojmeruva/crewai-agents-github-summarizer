
from django.urls import path
from . import views




urlpatterns = [
path('', views.documentation_interface, name='documentation_interface'),
    path('generate/', views.generate_documentation, name='generate_documentation'),
]