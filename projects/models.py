import datetime
from django.db import models
from clientdata.models import Client
from employees.models import Employee

# Create your models here.



class Project(models.Model):
    all_status = {
        "Pendiente": "Pendiente",
        "En progreso": "En progreso",
        "Completado": "Completado",
    }
    title = models.CharField(max_length=200)
    description = models.TextField()
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now=False, null=True, blank=True)
    created_by = models.CharField(max_length=100, null=True, blank=True)
    updated_at = models.DateField(auto_now=False)
    updated_by = models.CharField(max_length=100, null=True, blank=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=100, choices=all_status, default='Pendiente')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    car = models.ForeignKey('clientdata.Car', on_delete=models.CASCADE, null=True, blank=True)
    car_kms = models.CharField(max_length=100,null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.client.name}"
    
    class Meta:
        db_table = "projects"
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        ordering = ["-id"]




class Task(models.Model):
    all_status = {
        "Pendiente": "Pendiente",
        "En progreso": "En progreso",
        "Completado": "Completado",
    }
    title = models.CharField(max_length=200)
    description = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    created_by = models.CharField(max_length=100, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=False, null=True, blank=True)
    updated_by = models.CharField(max_length=100, null=True, blank=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=100, choices=all_status, default='Pendiente')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)


    def __str__(self):
        return f"{self.title} - {self.project.title}"
    
    class Meta:
        db_table = "tasks"
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        ordering = ["-id"]


class Comment(models.Model):

    task = models.ForeignKey(Task, on_delete=models.DO_NOTHING, blank=True, related_name='comments_intask')
    text = models.TextField(max_length=5000)
    created_by = models.CharField(max_length=100, null=False, blank=True, default="")
    created_at = models.DateTimeField(default=datetime.datetime.now())
    updated_by = models.CharField(max_length=100, null=False, blank=True, default="")
    updated_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.task.title + ' - ' + self.created_by}"
    
    class Meta:
        db_table = 'comments'
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ['-id']