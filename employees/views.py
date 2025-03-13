import datetime
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from .models import *
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
import logging
# Create your views here.



class EmployeesList(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'employees.view_employee'
    login_url = 'frontend:login'
    model = Employee
    template_name = 'employees.html'
    context_object_name = 'employees'
    def handle_no_permission(self):
        """Se ejecuta cuando el usuario no tiene permiso para acceder."""
        if self.request.user.is_authenticated:
            logging.error(f'Acceso denegado: El usuario {self.request.user.username} intentó acceder a la seccion de empleados sin permiso.')
        else:
            logging.error(f'Acceso denegado: Un usuario anónimo intentó acceder a la seccion de empleados sin permiso.')

        # Enviar mensaje al usuario
        messages.error(self.request, 'No tienes permisos para realizar esta acción.')

        # Si es una solicitud AJAX, responder con JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "error": "No tienes permisos para eliminar vehículos."}, status=403)
        
        # Para solicitudes normales, redirigir al login o a otra página
        return super().handle_no_permission()

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(position__icontains=search_query)
            )
        return queryset




class AddEmployee(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'employees.add_employee'
    login_url = 'frontend:login'
    model = Employee
    template_name = 'add_employee.html'
    fields = ['name', 'position']
    success_url = '/employees/'
    login_url = 'frontend:login'

    def handle_no_permission(self):
        """Se ejecuta cuando el usuario no tiene permiso para acceder."""
        if self.request.user.is_authenticated:
            logging.error(f'Acceso denegado: El usuario {self.request.user.username} intentó agregar un empleado sin permiso.')
        else:
            logging.error(f'Acceso denegado: Un usuario anónimo intentó agregar un empleado sin permiso.')

        # Enviar mensaje al usuario
        messages.error(self.request, 'No tienes permisos para realizar esta acción.')

        # Si es una solicitud AJAX, responder con JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "error": "No tienes permisos para eliminar vehículos."}, status=403)
        
        # Para solicitudes normales, redirigir al login o a otra página
        return super().handle_no_permission()

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Empleado agregado correctamente')
        logging.info(self.request.user.username + ' ha agregado un nuevo empleado.')

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": True})
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error al agregar el empleado. Por favor intentelo de nuevo.')
        logging.error(self.request.user.username + ' ha intentado agregar un empleado pero ha fallado.')

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "error": form.errors}, status=400)
        return super().form_invalid(form)


class UpdateEmployee(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'employees.change_employee'
    model = Employee
    template_name = 'edit_employee.html'
    fields = ['name', 'position']
    success_url = '/employees/'
    login_url = 'frontend:login'

    def handle_no_permission(self):
        current_employee = Employee.objects.get(pk=self.kwargs['pk'])
        """Se ejecuta cuando el usuario no tiene permiso para acceder."""
        if self.request.user.is_authenticated:
            logging.error(f'Acceso denegado: El usuario {self.request.user.username} intentó actualizar el empleado {current_employee.username} sin permiso.')
        else:
            logging.error(f'Acceso denegado: Un usuario anónimo intentó actualizar el empleado {current_employee.username} sin permiso.')

        # Enviar mensaje al usuario
        messages.error(self.request, 'No tienes permisos para realizar esta acción.')

        # Si es una solicitud AJAX, responder con JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "error": "No tienes permisos para eliminar vehículos."}, status=403)
        
        # Para solicitudes normales, redirigir al login o a otra página
        return super().handle_no_permission()
    
    def form_valid(self, form):
        current_employee = Employee.objects.get(pk=self.kwargs['pk'])
        form.save()
        messages.success(self.request, 'Empleado actualizado correctamente')
        logging.info(f'El usuario {self.request.user.username} ha actualizado el empleado {current_employee.username}.')

        # Respuesta AJAX
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": True})
        return super().form_valid(form)

    def form_invalid(self, form):
        current_employee = Employee.objects.get(pk=self.kwargs['pk'])
        messages.error(self.request, 'Error al actualizar el Empleado.')
        logging.error(f'El usuario {self.request.user.username} ha intentado actualizar el empleado {current_employee.username} pero ha fallado.')
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "error": form.errors.as_json()}, status=400)
        return super().form_invalid(form)
    


class DeleteEmployee(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'employees.delete_employee'
    model = Employee
    template_name = 'delete_employee.html'
    success_url = '/employees/'
    login_url = 'frontend:login'
    def handle_no_permission(self):
        current_employee = Employee.objects.get(pk=self.kwargs['pk'])
        """Se ejecuta cuando el usuario no tiene permiso para acceder."""
        if self.request.user.is_authenticated:
            logging.error(f'Acceso denegado: El usuario {self.request.user.username} intentó eliminar el empleado {current_employee.username} sin permiso.')
        else:
            logging.error(f'Acceso denegado: Un usuario anónimo intentó eliminar el empleado {current_employee.username} sin permiso.')

        # Enviar mensaje al usuario
        messages.error(self.request, 'No tienes permisos para realizar esta acción.')

        # Si es una solicitud AJAX, responder con JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "error": "No tienes permisos para eliminar vehículos."}, status=403)
        
        # Para solicitudes normales, redirigir al login o a otra página
        return super().handle_no_permission()

    def delete(self, request, *args, **kwargs):
        current_employee = Employee.objects.get(pk=self.kwargs['pk'])
        employee = self.get_object()  # Obtener el cliente a eliminar
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # Si es AJAX
            try:
                employee.delete()  # Eliminar el cliente
                logging.info(f'El usuario {self.request.user.username} ha eliminado el empleado {current_employee.username}.')  # Registrar el evento en el log
                return JsonResponse({"success": True, "message": "Empleado eliminado correctamente"})
            except Exception as e:
                # Enviar el mensaje de error si ocurre una excepción
                messages.error(self.request, f'Error al eliminar el Empleado: {str(e)}')  # Mensaje de error
                logging.error(f'El usuario {self.request.user.username} ha intentado eliminar el empleado {current_employee.username} pero ha fallado.')  # Registrar el evento
                return JsonResponse({"success": False, "error": str(e)}, status=400)

        # Si no es AJAX, procesar la solicitud normalmente
        messages.success(self.request, 'Empleado eliminado correctamente')
        logging.info(f'El usuario {self.request.user.username} ha eliminado el empleado {current_employee.username}.')  # Registrar el evento en el log
        return super().delete(request, *args, **kwargs)
