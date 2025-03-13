import asyncio
import calendar
from django.http import HttpResponse, JsonResponse
from django.utils.timezone import datetime, timedelta
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import ListView, CreateView, DeleteView, UpdateView, TemplateView, View
from django.contrib.auth.views import LoginView
from .forms import LoginForm
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models.functions import ExtractYear, ExtractMonth
from projects.models import Project
from django.db.models import Count
from django.db.models import Q
from management.models import Notification
import logging
# Create your views here.

class Login(LoginView):
    template_name = 'login.html'
    form_class = LoginForm
    fields = ['username', 'password']
    redirect_authenticated_user = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_success_url(self):
        return reverse_lazy('frontend:index')
    
    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        logger = logging.getLogger('django')
        logger.error(f'Se ha intentado acceder a la aplicacion con un usuario no registrado')
        messages.error(self.request, 'Usuario o password incorrectos. Inténtalo de nuevo.')
        return super().form_invalid(form)
    

class Index(LoginRequiredMixin, TemplateView):
    permission_required = 'frontend.view_index'
    template_name = 'index.html'
    login_url = 'frontend:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['last_projects'] = self.get_last_projects()
        context['next_services'] = self.get_next_services()

        # Obtener el año seleccionado del parámetro GET
        selected_year = self.request.GET.get('year', None)
        if not selected_year:
            selected_year = datetime.now().year
        # Obtener años para el desplegable
        context['years'] = self.get_years()

        # Si un año ha sido seleccionado, contamos los proyectos para ese año
        if selected_year:
            try:
                selected_year = int(selected_year)  # Convertir a entero si es necesario
                context['selected_year'] = selected_year
                context['projects_count'] = self.get_projects_count(selected_year)
                context['inprogress_projects'] = self.get_inprogress_projects(selected_year)  # Contar los proyectos en progreso para ese año
                context['completed_projects'] = self.get_completed_projects(selected_year)  # Contar los proyectos completados para ese año
                context['pending_projects'] = self.get_pending_projects(selected_year)  # Obtener los proyectos para es
                context['projects_count_per_month'] = self.get_projects_count_per_month(selected_year)
            except ValueError:
                context['selected_year'] = None
                context['projects_count'] = self.get_projects_count()  # Total sin filtro de año
                context['inprogress_projects'] = self.get_inprogress_projects()
                context['completed_projects'] = self.get_completed_projects()  # Total sin filtro de año
                context['pending_projects'] = self.get_pending_projects()
                context['projects_count_per_month'] = self.get_projects_count_per_month()
        else:
            context['selected_year'] = None
            context['projects_count'] = self.get_projects_count()  # Total sin filtro de año
            context['inprogress_projects'] = self.get_inprogress_projects()
            context['completed_projects'] = self.get_completed_projects()  # Total sin filtro de año
            context['pending_projects'] = self.get_pending_projects()
            context['projects_count_per_month'] = self.get_projects_count_per_month()

        return context

    def get_years(self):
        # Obtener los años distintos de los proyectos
        years = Project.objects.annotate(year=ExtractYear('end_date')).values_list('year', flat=True).distinct().order_by('-year')
        return years
    
    def get_projects_count(self, selected_year=None):
        if selected_year:
            # Filtrar los proyectos según el año seleccionado y contar
            projects_count = Project.objects.filter(end_date__year=selected_year).count()
        else:
            # Si no se seleccionó un año, contar todos los proyectos
            projects_count = Project.objects.count()
        return projects_count
    
    def get_inprogress_projects(self, selected_year=None):
        if selected_year:
            # Filtrar los proyectos según el año seleccionado y contar
            inprogress_projects = Project.objects.filter(end_date__year=selected_year, status='En Progreso').count()
        else:
            # Si no se seleccionó un año, contar todos los proyectos
            inprogress_projects = Project.objects.filter(status='In Progress').count()
        return inprogress_projects
    
    def get_completed_projects(self, selected_year=None):
        if selected_year:
            # Filtrar los proyectos según el año seleccionado y contar
            completed_projects = Project.objects.filter(end_date__year=selected_year, status='Completado').count()
        else:
            # Si no se seleccionó un año, contar todos los proyectos
            completed_projects = Project.objects.filter(status='Completed').count()
        return completed_projects
    
    def get_pending_projects(self, selected_year=None):
        if selected_year:
            # Filtrar los proyectos según el año seleccionado y contar
            pending_projects = Project.objects.filter(end_date__year=selected_year, status='Pendiente').count()
        else:
            # Si no se seleccionó un año, contar todos los proyectos        
            pending_projects = Project.objects.filter(status='Pending').count()
        return pending_projects
    
    import calendar
    
    def get_projects_count_per_month(self, selected_year=None):
        MONTHS_ES = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
        7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
        }
        if selected_year:
            projects_count_per_month = Project.objects.filter(end_date__year=selected_year) \
                .annotate(month=ExtractMonth('end_date')) \
                .values('month') \
                .annotate(count=Count('id')) \
                .order_by('month')
        else:
            projects_count_per_month = Project.objects.annotate(month=ExtractMonth('end_date')) \
                .values('month') \
                .annotate(count=Count('id')) \
                .order_by('month')
    
        project_counts_dict = {entry['month']: entry['count'] for entry in projects_count_per_month}
    
        # Convertir los meses a español
        result = [
            {'month': MONTHS_ES[i], 'count': project_counts_dict.get(i, 0)}
            for i in range(1, 13)
        ]
    
        return result
    

    def get_last_projects(self):
        last_projects = Project.objects.all().order_by('-id')[:5]
        return last_projects
    
    # def get_next_services(self):
    #     now = datetime.now().date()  # Solo la fecha, sin la hora
    #     one_year_ago = now - timedelta(days=365)  # Hace un año exacto
    #     almost_one_year = now - timedelta(days=355)  # Rango de 10 días antes del año exacto

    #     # Filtrando los proyectos que estén en el rango (dentro de 10 días antes de cumplir el año)
    #     # o que hayan pasado hace más de un año
    #     next_services = Project.objects.filter(
    #         Q(end_date__gte=almost_one_year, end_date__lt=one_year_ago) |  # Rango de 10 días antes de un año
    #         Q(end_date__lt=one_year_ago)  # Proyectos que ya han pasado de un año
    #     ).order_by('end_date')[:5]

    #     return next_services

    def get_next_services(self):
        notifications = Notification.objects.all().filter(notificated = False).order_by('-id')[:5]
        return notifications


    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        # if user.is_superuser:
            # return redirect('admin:index')
        if user.is_staff:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('projects:tasks')
        
