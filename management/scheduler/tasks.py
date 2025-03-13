from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from django.utils.timezone import localtime
import logging
from ..models import Notification
from projects.models import Project
from datetime import datetime, timedelta
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

def save_next_services_task():
    now = datetime.now().date()
    one_year_ago = now - timedelta(days=365)
    almost_one_year = now - timedelta(days=335)

    projects = Project.objects.filter(
        Q(end_date__gte=almost_one_year, end_date__lt=one_year_ago) |
        Q(end_date__lt=one_year_ago)
    ).order_by('-end_date')

    for project in projects:
        if not Notification.objects.filter(client=project.client, title=f'Recordatorio de servicio para {project.title}', car_kms=project.car_kms).exists():
            try:
                notification = Notification.objects.create(
                    title=f'Recordatorio de servicio para {project.title}',
                    client=project.client,
                    car=project.car,
                    car_kms=project.car_kms,
                    last_service_date=project.end_date,
                    notificated=False,
                )
                print(f'Notificación creada: {notification.pk} para {notification.client}')
            except IntegrityError:
                print(f'Error creando notificación para el proyecto {project.title}')
            except ObjectDoesNotExist:
                print(f'El cliente del proyecto {project.title} no existe.')
        else:
            print(f'La notificación para el proyecto {project.title} ya existe.')


def start():
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(save_next_services_task, 'interval', hours=24)  # Ejecuta cada 5 minutos
    scheduler.start()

    # Manejo de eventos de ejecución
    def job_listener(event):
        if event.exception:
            logging.error(f'La tarea {event.job_id} falló')
        else:
            logging.info(f'La tarea {event.job_id} fue ejecutada correctamente')

    # Conectamos el listener a los eventos
    scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)