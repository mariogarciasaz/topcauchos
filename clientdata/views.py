from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
import datetime
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from .models import *
from django.db.models import Q
from clientdata.forms import *
from django.contrib import messages
from projects.forms import Project, Task
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
import logging
from projects.forms import ProjectForm

# Create your views here.

class ClientsList(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'clientdata.view_client'
    login_url = 'frontend:login'
    model = Client
    template_name = 'clients.html'
    context_object_name = 'clients'

    def handle_no_permission(self):
        """Se ejecuta cuando el usuario no tiene permiso para acceder."""
        if self.request.user.is_authenticated:
            logging.error(f'Acceso denegado: El usuario {self.request.user.username} intentó acceder a la seccion de clientes sin permiso.')
        else:
            logging.error(f'Acceso denegado: Un usuario anónimo intentó acceder a la seccion de clientes sin permiso.')

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
                Q(email__icontains=search_query) |
                Q(phone__icontains=search_query) |
                Q(address__icontains=search_query)
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class AddClient(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'clientdata.add_client'
    login_url = 'frontend:login'
    model = Client
    template_name = 'add_client.html'
    form_class = ClientForm
    success_url = reverse_lazy('clients:clients')

    def handle_no_permission(self):
        """Se ejecuta cuando el usuario no tiene permiso para acceder."""
        if self.request.user.is_authenticated:
            logging.error(f'Acceso denegado: El usuario {self.request.user.username} intentó agregar un cliente sin permiso.')
        else:
            logging.error(f'Acceso denegado: Un usuario anónimo intentó agregar un cliente sin permiso.')

        # Enviar mensaje al usuario
        messages.error(self.request, 'No tienes permisos para realizar esta acción.')

        # Si es una solicitud AJAX, responder con JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "error": "No tienes permisos para eliminar vehículos."}, status=403)
        
        # Para solicitudes normales, redirigir al login o a otra página
        return super().handle_no_permission()

    def form_valid(self, form):
        created_at = datetime.datetime.now()
        form.instance.created_at = created_at
        form.save()
        messages.success(self.request, 'Cliente agregado correctamente')
        logging.info(f'El usuario {self.request.user.username} ha agregado un nuevo cliente.')

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": True})
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error al agregar el cliente. Intentelo de nuevo.')
        logging.error(f'El usuario {self.request.user.username} ha intentado agregar un cliente pero fallo.')

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "error": form.errors}, status=400)
        return super().form_invalid(form)


class UpdateClient(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'clientdata.change_client'
    login_url = 'frontend:login'
    model = Client
    template_name = 'update_client.html'
    form_class = ClientForm
    success_url = reverse_lazy('clientdata:clients')

    def handle_no_permission(self):
        current_user = Client.objects.get(pk=self.kwargs['pk'])
        """Se ejecuta cuando el usuario no tiene permiso para acceder."""
        if self.request.user.is_authenticated:
            logging.error(f'Acceso denegado: El usuario {self.request.user.username} intentó actualizar el cliente {current_user.name} sin permiso.')
        else:
            logging.error(f'Acceso denegado: Un usuario anónimo intentó actualizar el cliente {current_user.name} sin permiso.')

        # Enviar mensaje al usuario
        messages.error(self.request, 'No tienes permisos para realizar esta acción.')

        # Si es una solicitud AJAX, responder con JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "error": "No tienes permisos para eliminar vehículos."}, status=403)
        
        # Para solicitudes normales, redirigir al login o a otra página
        return super().handle_no_permission()

    def form_valid(self, form):
        current_user = Client.objects.get(pk=self.kwargs['pk'])
        updated_at = datetime.datetime.now()
        form.instance.updated_at = updated_at
        form.save()
        messages.success(self.request, 'Cliente actualizado correctamente')
        logging.info(f'El usuario {self.request.user.username} ha actualizado el cliente {current_user.name}.')

        # Respuesta AJAX
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": True})
        return super().form_valid(form)

    def form_invalid(self, form):
        current_user = Client.objects.get(pk=self.kwargs['pk'])
        messages.error(self.request, 'Error al actualizar el cliente.')
        logging.error(f'El usuario {self.request.user.username} ha intentado actualizar el cliente {current_user.name} pero fallo.')
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "error": form.errors.as_json()}, status=400)
        return super().form_invalid(form)



logger = logging.getLogger(__name__)

class DeleteClient(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'clientdata.delete_client'
    login_url = 'frontend:login'
    model = Client
    template_name = 'delete_client.html'
    success_url = reverse_lazy('clientdata:clients')

    def handle_no_permission(self):
        current_user = Client.objects.get(pk=self.kwargs['pk'])
        if self.request.user.is_authenticated:
            logger.error(f'Acceso denegado: El usuario {self.request.user.username} intentó eliminar el cliente {current_user.name} sin permiso.')
        else:
            logger.error(f'Acceso denegado: Un usuario anónimo intentó el cliente {current_user.name} sin permiso.')

        messages.error(self.request, 'No tienes permisos para realizar esta acción.')

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "error": "No tienes permisos para eliminar vehículos."}, status=403)

        return super().handle_no_permission()

    def delete(self, request, *args, **kwargs):
        current_user = Client.objects.get(pk=self.kwargs['pk'])
        client = self.get_object()
        logger.debug(f"Intentando eliminar el cliente: {client.name} (ID: {client.pk})")

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                client.delete()
                messages.success(self.request, 'Cliente eliminado correctamente')
                logger.info(f'El usuario {self.request.user.username} ha eliminado el cliente {current_user.name}.')
                return JsonResponse({"success": True, "message": "Cliente eliminado correctamente"})
            except Exception as e:
                logger.error(f'Error al eliminar el cliente {current_user.name}: {str(e)}', exc_info=True)
                messages.error(self.request, f'Error al eliminar el cliente: {str(e)}')
                return JsonResponse({"success": False, "error": str(e)}, status=400)

        messages.success(self.request, 'Cliente eliminado correctamente')
        logger.info(f'El usuario {self.request.user.username} ha eliminado el cliente {current_user.name}.')
        return super().delete(request, *args, **kwargs)


class CarsView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'clientdata.view_car'
    login_url = 'frontend:login'
    model = Car
    template_name = 'cars.html'
    context_object_name = 'cars'

    def handle_no_permission(self):
        """Se ejecuta cuando el usuario no tiene permiso para acceder."""
        if self.request.user.is_authenticated:
            logging.error(f'Acceso denegado: El usuario {self.request.user.username} intentó acceder a la vista de vehículos sin permiso.')
        else:
            logging.error(f'Acceso denegado: Un usuario anónimo intentó acceder a la vista de vehículos sin permiso.')

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
                Q(brand__icontains=search_query) |
                Q(model__icontains=search_query) |
                Q(year__icontains=search_query) |
                Q(color__icontains=search_query) |
                Q(license_plate__icontains=search_query) |
                Q(last_service_date__icontains=search_query)
            )
        return queryset
    

class AddCar(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'clientdata.add_car'
    login_url = 'frontend:login'
    model = Car
    form_class = CarForm
    login_url = 'frontend:login'
    success_url = reverse_lazy('clientdata:ClientData')

    def handle_no_permission(self):
        """Se ejecuta cuando el usuario no tiene permiso para acceder."""
        if self.request.user.is_authenticated:
            logging.error(f'Acceso denegado: El usuario {self.request.user.username} intentó agregar un vehículo sin permiso.')
        else:
            logging.error(f'Acceso denegado: Un usuario anónimo intentó agregar un vehículo.')

        # Enviar mensaje al usuario
        messages.error(self.request, 'No tienes permisos para realizar esta acción.')

        # Si es una solicitud AJAX, responder con JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "error": "No tienes permisos para eliminar vehículos."}, status=403)
        
        # Para solicitudes normales, redirigir al login o a otra página
        return super().handle_no_permission()

    def form_valid(self, form):
        car = form.save()
        messages.success(self.request, 'Vehículo agregado correctamente')
        logging.info(f'El usuario {self.request.user.username} ha agregado un nuevo vehículo.')

        # Verifica si la solicitud es AJAX
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'car_id': car.id})

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error al agregar el vehículo')
        logging.error(f'El usuario {self.request.user.username} ha intentado agregar un nuevo vehículo pero fallo.')

        # Si la solicitud es AJAX, devuelve los errores
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

        return super().form_invalid(form)

class UpdateCar(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'clientdata.change_car'
    login_url = 'frontend:login'
    model = Car
    template_name = 'edit_car.html'
    form_class = CarForm
    success_url = reverse_lazy('clientdata:ClientData')
    login_url = 'frontend:login'

    def handle_no_permission(self):
        current_car = Car.objects.get(pk=self.kwargs['pk'])
        """Se ejecuta cuando el usuario no tiene permiso para acceder."""
        if self.request.user.is_authenticated:
            logging.error(f'Acceso denegado: El usuario {self.request.user.username} intentó actualizar el vehículo {current_car.brand} {current_car.model} del cliente {current_car.client.name} sin permiso.')
        else:
            logging.error(f'Acceso denegado: Un usuario anónimo intentó actualizar el vehículo {current_car.brand} {current_car.model} del cliente {current_car.client.name}.')

        # Enviar mensaje al usuario
        messages.error(self.request, 'No tienes permisos para realizar esta acción.')

        # Si es una solicitud AJAX, responder con JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "error": "No tienes permisos para eliminar vehículos."}, status=403)
        
        # Para solicitudes normales, redirigir al login o a otra página
        return super().handle_no_permission()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        current_car = Car.objects.get(pk=self.kwargs['pk'])
        car = form.save(commit=False)

        # Si client no está en el formulario, usa el que ya tiene el objeto
        if not car.client:
            car.client = self.get_object().client

        car.save()
        logging.info(f'El usuario {self.request.user.username} ha actualizado el vehiculo {current_car.brand} {current_car.model} del cliente {current_car.client.name}.')
        messages.success(self.request, 'Vehiculo actualizado correctamente')
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'car': {
                    'id': car.id,
                    'brand': car.brand,
                    'model': car.model,
                    'year': car.year,
                    'color': car.color,
                    'license_plate': car.license_plate,
                    'last_service_date': car.last_service_date.strftime('%Y-%m-%d') if car.last_service_date else "",
                    'kms': car.kms
                }
            })

        return super().form_valid(form)

    def form_invalid(self, form):
        current_car = Car.objects.get(pk=self.kwargs['pk'])
        logging.error(f'El usuario {self.request.user.username} ha intentado actualizar el vehiculo {current_car.brand} {current_car.model} del cliente {current_car.client.name} pero fallo.')
        messages.error(self.request, 'Error al actualizar el vehículo')
        # Verificar si la solicitud es AJAX
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors})
        return super().form_invalid(form)



class DeleteCar(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'clientdata.delete_car'
    login_url = 'frontend:login'
    model = Car
    template_name = 'delete_car.html'
    success_url = reverse_lazy('clients:clients')  # Redirigir después de la eliminación

    def handle_no_permission(self):
        current_car = Car.objects.get(pk=self.kwargs['pk'])
        """Se ejecuta cuando el usuario no tiene permiso para acceder."""
        if self.request.user.is_authenticated:
            logging.error(f'Acceso denegado: El usuario {self.request.user.username} intentó eliminar el vehículo {current_car.brand} {current_car.model} del cliente {current_car.client.name} sin permiso.')
        else:
            logging.error(f'Acceso denegado: Un usuario anónimo intentó eliminar el vehículo {current_car.brand} {current_car.model} del cliente {current_car.client.name} sin permiso.')

        # Enviar mensaje al usuario
        messages.error(self.request, 'No tienes permisos para realizar esta acción.')

        # Si es una solicitud AJAX, responder con JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "error": "No tienes permisos para eliminar vehículos."}, status=403)
        
        # Para solicitudes normales, redirigir al login o a otra página
        return super().handle_no_permission()

    def delete(self, request, *args, **kwargs):
        current_car = Car.objects.get(pk=self.kwargs['pk'])
        car = self.get_object()  # Obtener el vehículo a eliminar
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # Si es una solicitud AJAX
            try:
                car.delete()  # Eliminar el vehículo
                messages.success(self.request, 'Vehículo eliminado correctamente')  # Mensaje de éxito
                logging.info(f'El usuario {self.request.user.username} ha eliminado el vehiculo {current_car.brand} {current_car.model} del cliente {current_car.client.name}.')
                return JsonResponse({"success": True, "message": "Vehículo eliminado correctamente"})
            except Exception as e:
                # Enviar el mensaje de error si ocurre una excepción
                messages.error(self.request, f'Error al eliminar el vehículo: {str(e)}')  # Mensaje de error
                logging.error(f'El usuario {self.request.user.username} ha intentado eliminar el vehiculo {current_car.brand} {current_car.model} del cliente {current_car.client.name} pero fallo.')
                return JsonResponse({"success": False, "error": str(e)}, status=400)

        # Si no es AJAX, procesar la solicitud normalmente
        return super().delete(request, *args, **kwargs)





@login_required(login_url='frontend:login')
@permission_required('clientdata.view_client')
def client_data(request, pk):
    client_data = get_object_or_404(Client, id=pk)

    # Filtrar solo los autos del cliente
    cars = Car.objects.filter(client_id=client_data.pk)
    projects = Project.objects.filter(client_id=client_data.pk)

    car_form = CarForm(initial={'client': client_data.pk})
    
    # 🔹 Pasa el queryset de autos del cliente a ProjectForm
    project_form = ProjectForm(client=client_data)  

    no_cars = not cars

    context = {
        'client': client_data,
        'cars': cars,
        'no_cars': no_cars,
        'car_form': car_form,
        'form': project_form,  
        'projects': projects,
    }
    print (project_form)

    return render(request, 'client.html', context)

@login_required(login_url='frontend:login')
@permission_required('clientdata.view_car')
def car_data(request, pk):
    car_data = get_object_or_404(Car, id=pk)
    all_projects = Project.objects.filter(car_id=car_data.pk)

    # Si hay proyectos, obtenemos los valores; si no, asignamos valores predeterminados
    latest_project_by_kms = all_projects.order_by('-car_kms').first()
    latest_project_by_date = all_projects.order_by('-end_date').first()

    current_kms = latest_project_by_kms.car_kms if latest_project_by_kms else 0
    last_service = latest_project_by_date.end_date if latest_project_by_date else "No hay registros"

    print(current_kms)

    context = {
        'car': car_data,
        'projects': all_projects,
        'current_kms': current_kms,
        'last_service': last_service
    }
    return render(request, 'car.html', context)


