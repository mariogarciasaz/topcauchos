from django.urls import path, include
from .views import *
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='frontend:login'), name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]