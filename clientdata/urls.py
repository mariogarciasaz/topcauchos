from django.urls import path, include
from .views import *
from . import views


urlpatterns = [
    path('client/<int:pk>', views.client_data, name='ClientData'),
    path('clients/', ClientsList.as_view(), name='clients'),
    path('clients/add/', AddClient.as_view(), name='add_client'),
    path('clients/edit/<int:pk>/', UpdateClient.as_view(), name='edit_client'),
    path('clients/delete/<int:pk>/', DeleteClient.as_view(), name='delete_client'),
    path ('cars', CarsView.as_view(), name='cars'),
    path ('cars/add_car/', AddCar.as_view(), name='add_car'),
    path ('cars/edit_car/<int:pk>/', UpdateCar.as_view(), name='edit_car'),
    path ('cars/delete/<int:pk>/', DeleteCar.as_view(), name='delete_car'),
    path ('car/<int:pk>/', views.car_data, name='CarData')
]