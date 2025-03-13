from django.urls import path, include
from .views import *
from . import views


urlpatterns = [
    path('', EmployeesList.as_view(), name='employees'),
    path('add/', AddEmployee.as_view(), name='add_employee'),
    path('edit/<int:pk>/', UpdateEmployee.as_view(), name='edit_employee'),
    path('delete/<int:pk>/', DeleteEmployee.as_view(), name='delete_employee'),
    
]