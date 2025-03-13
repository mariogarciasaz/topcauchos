from django.urls import path, include
from .views import *


urlpatterns = [
    path('notifications/', NotificationsView.as_view(), name='notifications'),
]