from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView, UpdateView, DetailView, TemplateView
from .models import *
from django.db.models import Q
from django.contrib import messages
from .forms import *
import datetime
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from clientdata.models import CarHistory, Car
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
import logging
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMessage

# Create your views here.



class ProjectsView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'projects.view_project'
    login_url = 'frontend:login'
    model = Project
    template_name = 'projects.html'
    context_object_name = 'projects'

    def handle_no_permission(self):
        """Se ejecuta cuando el usuario no tiene permiso para acceder."""
        if self.request.user.is_authenticated:
            logging.error(f'Acceso denegado: El usuario {self.request.user.username} intentó acceder a las seccion de proyectos sin permiso.')
        else:
            logging.error(f'Acceso denegado: Un usuario anónimo intentó acceder a las seccion de proyectos sin permiso.')

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
                Q(title__icontains=search_query) |
                Q(client__icontains=search_query) |
                Q(status__icontains=search_query) |
                Q(employee__icontains=search_query)
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ProjectForm()  # Agrega el formulario al contexto
        return context


class AddProject(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'projects.add_project'
    login_url = 'frontend:login'
    model = Project
    template_name = 'add_project.html'
    form_class = ProjectForm
    success_url = reverse_lazy('projects:projects')

    def handle_no_permission(self):
        """Se ejecuta cuando el usuario no tiene permiso para acceder."""
        if self.request.user.is_authenticated:
            logging.error(f'Acceso denegado: El usuario {self.request.user.username} intentó agregar un proyecto sin permiso.')
        else:
            logging.error(f'Acceso denegado: Un usuario anónimo intentó agregar un proyecto sin permiso.')

        # Enviar mensaje al usuario
        messages.error(self.request, 'No tienes permisos para realizar esta acción.')

        # Si es una solicitud AJAX, responder con JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "error": "No tienes permisos para acceder."}, status=403)
        
        # Para solicitudes normales, redirigir al login o a otra página
        return super().handle_no_permission()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
    
        client_id = self.request.GET.get('client')
        client = Client.objects.filter(pk=client_id).first() if client_id else None
    
        context['form'] = ProjectForm(client=client)
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        client_id = self.request.GET.get('client')
    
        print(f"Client ID: {client_id}")  # Verifica el client_id
    
        if client_id:
            cars = Car.objects.filter(client_id=client_id)
            print(f"Cars for client: {cars}") #Imprime los coches filtrados
            form.fields['car'].queryset = cars
        else:
            cars = Car.objects.all()
            print(f"All cars: {cars}") #Imprime todos los coches.
            form.fields['car'].queryset = cars
    
        print(f"Car field queryset: {form.fields['car'].queryset}") #Imprime el queryset final del campo car.
    
        return form

        
    def form_valid(self, form):
        print("Formulario recibido:", form.cleaned_data)
        form.instance.created_by = self.request.user.username
        form.instance.created_at = datetime.datetime.now()
        form.instance.updated_by = self.request.user.username
        form.instance.updated_at = datetime.datetime.now()
        form.instance.status = 'Pendiente'

        client = form.cleaned_data.get('client')
        car = form.cleaned_data.get('car')

        print(f" Cliente seleccionado: {client.id if client else 'Ninguno'}")
        print(f" Auto seleccionado: {car.id if car else 'Ninguno'}")

        if client and car:
            if car.client != client:
                logging.error(" ERROR: El auto seleccionado no pertenece al cliente")
                return JsonResponse(
                    {"success": False, "error": {"car": [{"message": "El vehículo seleccionado no pertenece a este cliente.", "code": "invalid_choice"}]}},
                    status=400
                )

        form.save()
        logging.info(f"El usuario {self.request.user.username} ha agregado un nuevo proyecto.")
        messages.success(self.request, 'Proyecto agregado correctamente')

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": True})

        return super().form_valid(form)



    def form_invalid(self, form):
        logging.error(self.request.user.username + ' ha intentado agregar un proyecto pero ha fallado.')

        # 🔹 Agrega los errores del formulario en el mensaje
        errors = form.errors.as_json()
        messages.error(self.request, 'Error al agregar el proyecto. Inténtalo de nuevo.')

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "error": errors}, status=400)

        return super().form_invalid(form)
    
    # def save_car_project(self, car, project):
    #     car_history = CarHistory.objects.create(
    #         car=car,
    #         service=project,
    #     )
    #     return car_history




@permission_required('projects.change_project', raise_exception=True)
@login_required
def edit_project(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form = ProjectForm(request.POST, instance=project, client=project.client)

        if form.is_valid():
            form.instance.updated_by = request.user.username
            form.instance.updated_at = timezone.now()
            form.save()
            return JsonResponse({'success': True})
        else:
            # Captura los errores si el formulario no es válido
            print("Form errors:", form.errors)  # Esto imprime en el log del servidor
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

    
    # def get_form(self, form_class=None):
    #     form = super().get_form(form_class)

    #     if not self.request.user.is_staff and not self.request.user.is_superuser:
    #         form.fields['username'].disabled = True
    #         form.fields['description'].disabled = True
    #         form.fields['start_date'].disabled = True
    #         form.fields['end_date'].disabled = True
    #         form.fields['status'].disabled = True
    #         form.fields['employee'].disabled = True
    #     return form


class DeleteProject(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'projects.delete_project'
    login_url = 'frontend:login'
    model = Project
    success_url = reverse_lazy('projects:projects')  # Se usa solo si NO es AJAX


    def handle_no_permission(self):
        current_project = Project.objects.get(pk=self.kwargs['pk'])
        """Se ejecuta cuando el usuario no tiene permiso para acceder."""
        if self.request.user.is_authenticated:
            logging.error(f'Acceso denegado: El usuario {self.request.user.username} intentó eliminar el proyecto {current_project.title} del cliente {current_project.client.name} sin permiso.')
        else:
            logging.error(f'Acceso denegado: Un usuario anónimo intentó eliminar el proyecto {current_project.title} del cliente {current_project.client.name} sin permiso.')

        # Enviar mensaje al usuario
        messages.error(self.request, 'No tienes permisos para realizar esta acción.')

        # Si es una solicitud AJAX, responder con JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "error": "No tienes permisos para eliminar vehículos."}, status=403)
        
        # Para solicitudes normales, redirigir al login o a otra página
        return super().handle_no_permission()

    def post(self, request, *args, **kwargs):
        current_project = Project.objects.get(pk=self.request.GET.get('pk'))
        # Obtenemos el comentario a eliminar
        project = self.get_object()

        # Verificamos si el usuario tiene permisos para eliminar el comentario
        if not request.user.has_perm('comments.delete_comment'):
            logging.error(f'Acceso denegado: El usuario {request.user.username} intentó eliminar el proyecto {current_project.title} del cliente {current_project.client.name} sin permiso.')
            return JsonResponse({'success': False, 'message': "No tienes permiso para eliminar este proyecto."}, status=403)
        
        # Eliminamos el comentario
        project.delete()
        logging.info(f'El usuario {self.request.user.username} ha eliminado el proyecto {current_project.title} del cliente {current_project.client.name}.')
        messages.success(request, "Proyecto eliminado correctamente.")
        
        # Retornamos una respuesta JSON para el frontend
        return JsonResponse({'success': True, 'message': "Proyecto eliminado correctamente"})

class ProjectDetails(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = 'projects.view_project'
    login_url = 'frontend:login'
    model = Project
    template_name = 'project_details.html'
    login_url = 'frontend:login'

    def handle_no_permission(self):
        current_project = Project.objects.get(pk=self.kwargs['pk'])
        """Se ejecuta cuando el usuario no tiene permiso para acceder."""
        if self.request.user.is_authenticated:
            logging.error(f'Acceso denegado: El usuario {self.request.user.username} intentó acceder a los detalles del proyecto {current_project.title} del cliente {current_project.client.name} sin permiso.')
        else:
            logging.error(f'Acceso denegado: Un usuario anónimo intentó acceder a los detalles del proyecto {current_project.title} del cliente {current_project.client.name} sin permiso.')

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
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(status__icontains=search_query) |
                Q(employee__icontains=search_query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object() # Obtener el objeto project
        context['project'] = project
        context['project_id'] = project.pk
        context['description'] = project.description
        context['client'] = project.client
        context['car'] = project.car
        context['employee'] = project.employee
        context['status'] = project.status
        context['start_date'] = project.start_date
        context['end_date'] = project.end_date
        context['created_at'] = project.created_at
        context['updated_at'] = project.updated_at
        context['created_by'] = project.created_by
        context['updated_by'] = project.updated_by
        context['tasks'] = self.get_tasks(context)
        context = self.get_total_tasks(context)
        context = self.get_pending_tasks(context)
        context = self.get_inprogress_tasks(context)
        context = self.get_completed_tasks(context)
        context['form'] = TaskForm(project=project)  # Agrega el formulario TaskForm al contexto
        return context

    def get_tasks(self, context):
        tasks = Task.objects.filter(project=context['project'])
        return tasks

    def get_total_tasks(self, context):
        total_tasks = Task.objects.filter(project=context['project']).count()
        context['total_tasks'] = total_tasks
        return context

    def get_pending_tasks(self, context):
        pending_tasks = Task.objects.filter(project=context['project'], status='Pendiente').count()
        context['pending_tasks'] = pending_tasks
        return context

    def get_completed_tasks(self, context):
        completed_tasks = Task.objects.filter(project=context['project'], status='Completado').count()
        context['completed_tasks'] = completed_tasks
        return context

    def get_inprogress_tasks(self, context):
        inprogress_tasks = Task.objects.filter(project=context['project'], status='En progreso').count()
        context['inprogress_tasks'] = inprogress_tasks
        return context

    def post(self, request, *args, **kwargs):
        """Maneja la solicitud POST para enviar el reporte del proyecto."""
        try:
            self.send_report()
            return HttpResponseRedirect(reverse('projects:project_details', kwargs={'pk': self.kwargs['pk']}))
        except Exception as e:
            messages.error(self.request, f'Error al enviar el correo al cliente: {str(e)}')
            logging.error(f'Error al enviar el reporte del proyecto {self.kwargs["pk"]} al cliente: {str(e)}')
            return HttpResponseRedirect(reverse('projects:project_details', kwargs={'pk': self.kwargs['pk']}))


    def send_report(self):
        project = Project.objects.get(pk=self.kwargs['pk'])
        tasks = Task.objects.filter(project=project)
        subject = f"Reporte del servicio de su vehiculo: {project.car} "
        message = render_to_string(
            'emails/project_report_email.html',
            {'project': project, 'tasks': tasks}
        )
        from_email = 'pruebatopcauchos@gmail.com'
        recipient_list = [project.client.email]
        try:
            email = EmailMessage(
                subject=subject,
                body=message,
                from_email=from_email,
                to=recipient_list,
            )
            email.content_subtype = "html"  # Especificar que el contenido es HTML
            email.send()
            messages.success(self.request, f'El reporte del proyecto {project.title} ha sido enviado al cliente {project.client.name}')
            logging.info(f'El reporte del proyecto {project.title} ha sido enviado al cliente {project.client.name}')
        except Exception as e:
            messages.error(self.request, f'Error al enviar el correo al cliente: {str(e)}')
            logging.error(f'Error al enviar el reporte del proyecto {project.title} al cliente: {project.client.name} - {str(e)}')


def email_report(request):
    project = Project.objects.all().first()
    tasks = Task.objects.filter(project=project)
    context = {
        'project': project,
        'tasks': tasks,
    }
    return render (request, 'emails/project_report_email.html', context)

class Tasks(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'projects.view_task'
    login_url = 'frontend:login'
    model = Task
    template_name = 'tasks.html'
    context_object_name = 'tasks'

    def handle_no_permission(self):
        """Se ejecuta cuando el usuario no tiene permiso para acceder."""
        if self.request.user.is_authenticated:
            logging.error(f'Acceso denegado: El usuario {self.request.user.username} intentó acceder a las tareas sin permiso.')
        else:
            logging.error(f'Acceso denegado: Un usuario anónimo intentó acceder a las tareas sin permiso.')

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
            queryset = Task.objects.filter(
                Q(id__icontains=search_query) |
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(project__icontains=search_query) |
                Q(status__icontains=search_query)
            )
        
        return queryset
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['tasks'] = self.get_queryset()


        context = self.get_all_tasks(context)
        context = self.get_pending_tasks(context)
        context = self.get_inprogress_tasks(context)
        context = self.get_completed_tasks(context)

        return context
    

    def get_all_tasks(self, context):

        tasks = Task.objects.all().count()

        context['all_tasks'] = tasks

        return context
    


    def get_pending_tasks(self, context):

        pending_tasks = Task.objects.filter(status='Pending').count()

        context['pending_tasks'] = pending_tasks

        return context
    

    def get_inprogress_tasks(self, context):

        inprogress_tasks = Task.objects.filter(status='In progress').count()

        context['inprogress_tasks'] = inprogress_tasks

        return context
    

    def get_completed_tasks(self, context):

        completed_tasks = Task.objects.filter(status='Completed').count()

        context['completed_tasks'] = completed_tasks

        return context
    
    


class MyTasks(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'projects.view_task'
    permission_denied_message = "You don't have permission to access, please contact with your administrator"
    login_url = 'frontend:login'
    model = Task
    template_name = 'my_tasks.html'
    context_object_name = 'tasks'

    def handle_no_permission(self):
        """Se ejecuta cuando el usuario no tiene permiso para acceder."""
        if self.request.user.is_authenticated:
            logging.error(f'Acceso denegado: El usuario {self.request.user.username} intentó acceder a la seccion de tareas sin permiso.')
        else:
            logging.error(f'Acceso denegado: Un usuario anónimo intentó acceder a la seccion de tareas sin permiso.')

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
            queryset = Task.objects.filter(
                Q(id__icontains=search_query) |
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(project__icontains=search_query) |
                Q(status__icontains=search_query)
            )
        
        return queryset
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        
        context['tasks'] = self.get_user_tasks()

        context = self.get_all_tasks(context)
        context = self.get_pending_tasks(context)
        context = self.get_inprogress_tasks(context)
        context = self.get_completed_tasks(context)

        return context
    

    def get_all_tasks(self, context):

        tasks = Task.objects.all().count()

        context['all_tasks'] = tasks

        return context
    


    def get_pending_tasks(self, context):

        pending_tasks = Task.objects.filter(status='Pending').count()

        context['pending_tasks'] = pending_tasks

        return context
    

    def get_inprogress_tasks(self, context):

        inprogress_tasks = Task.objects.filter(status='In progress').count()

        context['inprogress_tasks'] = inprogress_tasks

        return context
    

    def get_completed_tasks(self, context):

        completed_tasks = Task.objects.filter(status='Completed').count()

        context['completed_tasks'] = completed_tasks

        return context
    
    def get_user_tasks(self):

        tasks = Task.objects.filter(employee=self.request.user)

        return tasks



class ViewTask(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = 'projects.view_task'
    permission_denied_message = "You don't have permission to access, please contact with your administrator"
    login_url = 'frontend:login'
    model = Task
    template_name = 'view_task.html'
    context_object_name = 'task'

    def handle_no_permission(self):
        current_task = Task.objects.get(pk=self.kwargs['pk'])
        if self.request.user.is_authenticated:
            logging.error(f'Acceso denegado: El usuario {self.request.user.username} intentó acceder a la tarea {current_task.title} del proyecto {current_task.project.title} del cliente {current_task.project.client.name} sin permiso.')
        else:
            logging.error(f'Acceso denegado: Un usuario anónimo intentó acceder a la tarea {current_task.title} del proyecto {current_task.project.title} del cliente {current_task.project.client.name} sin permiso.')
        messages.error(self.request, 'No tienes permisos para realizar esta acción.')
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "error": "No tienes permisos para eliminar vehículos."}, status=403)
        return super().handle_no_permission()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = self.request.user

        if employee.is_staff or employee.is_superuser:
            task = get_object_or_404(Task, pk=kwargs['pk'])
        else:
            task = get_object_or_404(Task, pk=kwargs['pk'], employee=employee)

        context['task'] = task
        context['description'] = task.description
        context['project'] = task.project
        context['employee'] = task.employee
        context['status'] = task.status
        context['start_date'] = task.start_date
        context['end_date'] = task.end_date
        context['created_by'] = task.created_by
        context['updated_by'] = task.updated_by
        context['created_at'] = task.created_at
        context['updated_at'] = task.updated_at
        context['comments'] = self.get_comments(task)
        context['my_tasks'] = self.get_my_tasks(employee)
        context['form'] = CommentForm()  # Añade el formulario al contexto

        return context

    def get_comments(self, task):
        return Comment.objects.filter(task_id=task.id)

    def get_my_tasks(self, employee):
        return Task.objects.filter(employee=employee)




class Createtask(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'projects.add_task'
    permission_denied_message = "You don't have permission to access, please contact with your administrator"
    login_url = 'frontend:login'
    model = Task
    form_class = TaskForm
    template_name = 'create_task.html'
    success_url = reverse_lazy('tasks:tasks')

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            logging.error(f'Acceso denegado: El usuario {self.request.user.username} intentó crear una tarea sin permiso.')
        else:
            logging.error(f'Acceso denegado: Un usuario anónimo intentó crear una tarea sin permiso.')
        messages.error(self.request, 'No tienes permisos para realizar esta acción.')
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "error": "No tienes permisos para eliminar vehículos."}, status=403)
        return super().handle_no_permission()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = TaskForm()
        context['form'] = form
        return context

    def form_valid(self, form):
        form.instance.created_by = self.request.user.username
        form.instance.updated_by = ""
        try:
            if form.instance.end_date and form.instance.start_date and form.instance.end_date < form.instance.start_date:
                raise Exception("La fecha de finalizacion no puede ser menor que la fecha de inicio.")
            elif form.instance.status in ['En Progreso', 'Completado']:
                raise Exception(f"El estado no puede ser {form.instance.status}.")
            else:
                form.save()
                messages.success(self.request, 'Tarea creada correctamente')
                logging.info(f'El usuario {self.request.user.username} ha creado una nueva tarea.')
                if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({"success": True})
        except Exception as e:
            error_message = str(e)
            messages.error(self.request, 'No se ha podido crear la tarea. Inténtalo de nuevo.')
            logging.error(f'El usuario {self.request.user.username} intentó crear una tarea pero fallo: {error_message}')
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({"success": False, "error": error_message}, status=400)
            return render(self.request, self.template_name, {'form': form, 'error_message': error_message})
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error al crear la tarea. Inténtalo de nuevo.')
        logging.error(f'El usuario {self.request.user.username} intentó crear una tarea pero fallo: {form.errors}')
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "error": form.errors}, status=400)
        return super().form_invalid(form)


@login_required
@permission_required('projects.change_task', raise_exception=True)
def edit_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)

    if request.method == 'POST':
        print(request.POST)
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.instance.updated_by = request.user.username
            try:
                if form.instance.end_date < form.instance.start_date:
                    return JsonResponse({"success": False, "error": "La fecha de finalización no puede ser menor que la fecha de inicio."}, status=400)
                elif form.instance.status in ['En Progreso', 'Completed']:
                    return JsonResponse({"success": False, "error": "El estado no puede ser 'En Progreso' o 'Completado'."}, status=400)
                else:
                    form.save()
                    logging.info(f'El usuario {request.user.username} ha actualizado la tarea {task.title} del proyecto {task.project.title} del cliente {task.project.client.name}')
                    return JsonResponse({"success": True})
            except Exception as e:
                return JsonResponse({"success": False, "error": str(e)}, status=400)
        else:
            print(form.errors)
            logging.error(f'El usuario {request.user.username} ha intentado actualizar la tarea {task.title} pero fallo. Errores: {form.errors}')
            return JsonResponse({"success": False, "error": form.errors}, status=400)
    else:
        return JsonResponse({"success": False, "error": "Método no permitido"}, status=405)
    
    # def get_form(self, form_class=None):

    #     form = super().get_form(form_class)
    #     print(form.initial)
    #     current_data = Task.objects.get(pk=self.kwargs['pk'])

    #     if self.request.user.is_staff or self.request.user.is_superuser:
    #         pass
    #     else:
    #         form.fields['status'].disabled = True

    #     if self.request.user.username == current_data.employee or self.request.user.is_staff or self.request.user.is_superuser:
    #         pass
    #     else:
    #         form.fields['title'].disabled = True
    #         form.fields['description'].disabled = True
    #         form.fields['start_date'].disabled = True
    #         form.fields['end_date'].disabled = True
    #         form.fields['status'].disabled = True
    #         form.fields['employee'].disabled = True
    #         form.fields['project'].disabled = True


    #     return form



class Deletetask(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'projects.delete_task'
    permission_denied_message = "You don't have permission to access, please contact with your administrator"
    login_url = 'frontend:login'
    model = Task
    template_name = 'delete_task.html'
    success_url = reverse_lazy('tasks:tasks')

    def handle_no_permission(self):
        current_task = Task.objects.get(pk=self.kwargs['pk'])
        """Se ejecuta cuando el usuario no tiene permiso para acceder."""
        if self.request.user.is_authenticated:
            logging.error(f'Acceso denegado: El usuario {self.request.user.username} intentó eliminar la tarea {current_task.title} del proyecto {current_task.project.title} sin permiso.')
        else:
            logging.error(f'Acceso denegado: Un usuario anónimo intentó eliminar la tarea {current_task.title} del proyecto {current_task.project.title} sin permiso.')

        # Enviar mensaje al usuario
        messages.error(self.request, 'No tienes permisos para realizar esta acción.')

        # Si es una solicitud AJAX, responder con JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "error": "No tienes permisos para eliminar vehículos."}, status=403)
        
        # Para solicitudes normales, redirigir al login o a otra página
        return super().handle_no_permission()

    def post(self, request, *args, **kwargs):
        # Obtenemos el comentario a eliminar
        task = self.get_object()
        current_task = Task.objects.get(pk=self.kwargs['pk'])

        # Verificamos si el usuario tiene permisos para eliminar el comentario
        if not request.user.has_perm('tasks.delete_comment'):
            logging.error(f'El usuario {self.request.user.username} intento eliminar la tarea {current_task.title} del proyecto {current_task.project.title} sin permiso.')
            return JsonResponse({'success': False, 'message': "No tienes permiso para eliminar esta tarea."}, status=403)
        
        # Eliminamos el comentario
        task.delete()
        logging.info(f'El usuario {self.request.user.username} ha eliminado la tarea {current_task.title} del proyecto {current_task.project.title}.')
        messages.success(request, "Comentario eliminado correctamente.")
        
        # Retornamos una respuesta JSON para el frontend
        return JsonResponse({'success': True, 'message': "Tarea eliminada correctamente"})



#COMMENTS VIEWS

class CreateComment(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'projects.add_comment'
    permission_denied_message = "You don't have permission to access, please contact with your administrator"
    login_url = 'frontend:login'
    model = Comment
    form_class = CommentForm
    template_name = 'create_comment.html'
    success_url = reverse_lazy('tasks:tasks')

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            logging.error(f'Acceso denegado: El usuario {self.request.user.username} intentó crear un comentario sin permiso.')
        else:
            logging.error(f'Acceso denegado: Un usuario anónimo intentó crear un comentario sin permiso.')
        messages.error(self.request, 'No tienes permisos para realizar esta acción.')
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "error": "No tienes permisos para crear comentario."}, status=403)
        return super().handle_no_permission()

    def form_valid(self, form):
        task_id = self.request.GET.get('task_id')  # Obtiene task_id de los parámetros GET
        if task_id:
            task = get_object_or_404(Task, pk=task_id)
            form.instance.task = task
            form.instance.created_by = self.request.user.username
            form.instance.updated_by = ""
            try:
                form.save()
                messages.success(self.request, 'Comentario creado correctamente')
                logging.info(f'El usuario {self.request.user.username} ha creado un nuevo comentario para la tarea {task.title}.')
                if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({"success": True})
            except Exception as e:
                error_message = str(e)
                messages.error(self.request, 'No se ha podido crear el comentario. Inténtalo de nuevo.')
                logging.error(f'El usuario {self.request.user.username} intentó crear un comentario pero fallo: {error_message}')
                if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({"success": False, "error": error_message}, status=400)
                return render(self.request, self.template_name, {'form': form, 'error_message': error_message})
            return super().form_valid(form)
        else:
            messages.error(self.request, 'No se ha proporcionado el ID de la tarea.')
            logging.error(f'El usuario {self.request.user.username} intentó crear un comentario sin proporcionar el ID de la tarea.')
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({"success": False, "error": "No se ha proporcionado el ID de la tarea."}, status=400)
            return render(self.request, self.template_name, {'form': form, 'error_message': "No se ha proporcionado el ID de la tarea."})

    def form_invalid(self, form):
        messages.error(self.request, 'Error al crear el comentario. Inténtalo de nuevo.')
        logging.error(f'El usuario {self.request.user.username} intentó crear un comentario pero fallo: {form.errors}')
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "error": form.errors}, status=400)
        return super().form_invalid(form)





class comment_added(TemplateView):
    permission_required = 'projects.add_comment'
    permission_denied_message = "You don't have permission to access, please contact with your administrator"
    login_url = 'frontend:login'
    template_name = 'comment_added.html'
    


class UpdateComment(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'projects.change_comment'
    permission_denied_message = "You don't have permission to access, please contact with your administrator"
    login_url = 'frontend:login'
    model = Comment
    form_class = CommentForm
    template_name = 'update_comment.html'
    
    def handle_no_permission(self):
        current_comment = Comment.objects.get(pk=self.kwargs['pk'])
        """Se ejecuta cuando el usuario no tiene permiso para acceder."""
        if self.request.user.is_authenticated:
            logging.error(f'Acceso denegado: El usuario {self.request.user.username} intentó actualizar el comentario {current_comment.text} de la tarea {current_comment.task.title} del proyecto {current_comment.task.project.title} sin permiso.')
        else:
            logging.error(f'Acceso denegado: Un usuario anónimo actualizar el comentario {current_comment.text} de la tarea {current_comment.task.title} del proyecto {current_comment.task.project.title} sin permiso.')

        # Enviar mensaje al usuario
        messages.error(self.request, 'No tienes permisos para realizar esta acción.')

        # Si es una solicitud AJAX, responder con JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "error": "No tienes permisos para eliminar vehículos."}, status=403)
        
        # Para solicitudes normales, redirigir al login o a otra página
        return super().handle_no_permission()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm(instance=self.get_object())
        context['comment'] = self.get_object()  # Obtener el comentario actual
        return context

    def form_valid(self, form):
        current_comment = Comment.objects.get(pk=self.kwargs['pk'])
        form.instance.updated_by = self.request.user.username  # Solo actualizar el usuario
        logging.info(f'El usuario {self.request.user.username} ha actualizado el comentario {current_comment.text} de la tarea {current_comment.task.title} del proyecto {current_comment.task.project.title}.')
        messages.success(self.request, 'Comentario actualizado correctamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        current_comment = Comment.objects.get(pk=self.kwargs['pk'])
        logging.error(f'El usuario {self.request.user.username} ha intentado actualizar el comentario {current_comment.text} de la tarea {current_comment.task.title} del proyecto {current_comment.task.project.title} pero fallo.')
        messages.error(self.request, 'Error al actualizar el comentario.')
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    
    def post(self, request, *args, **kwargs):
        current_comment = Comment.objects.get(pk=self.kwargs['pk'])
        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            form.instance.updated_by = request.user.username
            form.save()
            logging.info(f'El usuario {self.request.user.username} ha actualizado el comentario {current_comment.text} de la tarea {current_comment.task.title} del proyecto {current_comment.task.project.title}.')
            messages.success(self.request, 'Comentario actualizado correctamente.')
            return JsonResponse({'success': True, 'message': 'Comentario actualizado correctamente'})
        else:
            response = JsonResponse({'success': False, 'errors': form.errors})
            response.status_code = 400  # Respuesta HTTP 400 en caso de error
            logging.error(f'El usuario {self.request.user.username} ha intentado actualizar el comentario {current_comment.text} de la tarea {current_comment.task.title} del proyecto {current_comment.task.project.title} pero fallo.')
            messages.error(self.request, 'Error al actualizar el comentario.')
            return response




class DeleteComment(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'projects.delete_comment'
    login_url = 'frontend:login'
    model = Comment
    template_name = 'delete_comment.html'

    def handle_no_permission(self):
        current_comment = Comment.objects.get(pk=self.kwargs['pk'])
        """Se ejecuta cuando el usuario no tiene permiso para acceder."""
        if self.request.user.is_authenticated:
            logging.error(f'Acceso denegado: El usuario {self.request.user.username} intentó actualizar el comentario {current_comment.text} de la tarea {current_comment.task.title} del proyecto {current_comment.task.project.title} sin permiso.')
        else:
            logging.error(f'Acceso denegado: Un usuario anónimo actualizar el comentario {current_comment.text} de la tarea {current_comment.task.title} del proyecto {current_comment.task.project.title} sin permiso.')

        # Enviar mensaje al usuario
        messages.error(self.request, 'No tienes permisos para realizar esta acción.')

        # Si es una solicitud AJAX, responder con JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "error": "No tienes permisos para eliminar vehículos."}, status=403)
        
        # Para solicitudes normales, redirigir al login o a otra página
        return super().handle_no_permission()

    def post(self, request, *args, **kwargs):
        # Obtenemos el comentario a eliminar
        comment = self.get_object()
        current_comment = Comment.objects.get(pk=self.kwargs['pk'])

        # Verificamos si el usuario tiene permisos para eliminar el comentario
        if not request.user.has_perm('comments.delete_comment'):
            logging.error(f'Acceso denegado: El usuario {request.user.username} intentó eliminar el comentario {current_comment.text} de la tarea {current_comment.task.title} del proyecto {current_comment.task.project.title} sin permiso.')
            return JsonResponse({'success': False, 'message': "No tienes permiso para eliminar este comentario."}, status=403)
        
        # Eliminamos el comentario
        comment.delete()
        messages.success(request, "Comentario eliminado correctamente.")
        logging.info(f'El usuario {self.request.user.username} ha eliminado el comentario {current_comment.text} de la tarea {current_comment.task.title} del proyecto {current_comment.task.project.title}.')
        
        # Retornamos una respuesta JSON para el frontend
        return JsonResponse({'success': True, 'message': "Comentario eliminado correctamente"})