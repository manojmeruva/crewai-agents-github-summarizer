
from django.urls import path
from . import views


# Task 4: Add the URL of the documentation_interface view
# Task 11: Add the URL of the generate_documentation view
urlpatterns = [
path('', views.documentation_interface, name='documentation_interface'),
]