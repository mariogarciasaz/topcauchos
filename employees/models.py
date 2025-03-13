from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

# Create your models here.


class Employee(AbstractUser):
    position = models.CharField(max_length=100)
    

    class Meta:
        db_table = 'employees_customuser'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-id']