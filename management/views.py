from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.utils.timezone import datetime, timedelta
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from .models import Notification
from projects.models import Project
from django.db.models import Q
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.shortcuts import redirect
from django.urls import reverse
from employees.models import Employee
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
import logging


# Create your views here.




class NotificationsView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    login_url = 'frontend:login'
    permission_required = 'management.view_notification'
    model = Notification
    template_name = 'notifications.html'
    context_object_name = 'notifications'
    paginate_by = 10  # Agrega paginación

    def get_queryset(self):
        queryset = super().get_queryset().filter(notificated=False)  # Filtra por notificaciones no enviadas
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(id__icontains=search_query) |
                Q(client__name__icontains=search_query) |
                Q(car__brand__icontains=search_query) |
                Q(car__model__icontains=search_query)
            )
        print(queryset.query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # No sobrescribas 'notifications', ya está en el contexto por ListView
        # Si necesitas get_next_services() para otra cosa, puedes agregarlo así:
        # context['next_services'] = self.get_next_services() 
        return context

    def post(self, request, *args, **kwargs):
        notification_id = request.POST.get('notification_id')
        notification = get_object_or_404(Notification, pk=notification_id)

        try:
            self.send_client_email(notification)
            self.send_admin_email(notification)
            notification.notificated = True
            notification.save()
            messages.success(self.request, f'Notificación {notification.id} enviada con éxito.')
        except Exception as e:
            messages.error(self.request, f'Error al enviar la notificación: {str(e)}')
            logging.error(f'Error al enviar la notificación {notification.id}: {str(e)}')

        return HttpResponseRedirect(reverse('management:notifications'))

    def send_client_email(self, notification):
        subject = "Recordatorio de Servicio"
        message = render_to_string(
            'emails/client_notification.html',
            {'notification': notification}
        )
        from_email = 'pruebatopcauchos@gmail.com'
        recipient_list = [notification.client.email]
        self.send_email(subject, message, from_email, recipient_list)
        messages.success(self.request, f'Notificación enviada al cliente {notification.client}')
        logging.info(f'Notificación enviada al cliente {notification.client}')

    def send_admin_email(self, notification):
        admins = Employee.objects.filter(is_staff=True)
        subject = "Recordatorio enviado al cliente"
        message = render_to_string(
            'emails/admin_notification.html',
            {'notification': notification}
        )
        from_email = 'pruebatopcauchos@gmail.com'
        recipient_list = [admin.email for admin in admins]
        self.send_email(subject, message, from_email, recipient_list)
        messages.success(self.request, 'Notificación enviada a los administradores')
        logging.info(f'Notificación enviada a los administradores')

    def send_email(self, subject, message, from_email, recipient_list):
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=from_email,
            to=recipient_list,
        )
        email.content_subtype = "html"
        email.send()
    


# def email_view(request):
#     # Suponiendo que tienes al menos un notification
#     notification = Notification.objects.first()  # Puedes obtener una de ejemplo

#     return render(request, 'emails/client_notification.html', {'notification': notification})

# def email_view_admin(request):
#     # Suponiendo que tienes al menos un notification
#     notification = Notification.objects.first()  # Puedes obtener una de ejemplo

#     return render(request, 'emails/admin_notification.html', {'notification': notification})