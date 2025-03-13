from django.db import models
from clientdata.models import Client
# Create your models here.


class Notification(models.Model):
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    car = models.ForeignKey('clientdata.Car', on_delete=models.CASCADE, null=True, blank=True)
    car_kms = models.CharField(max_length=100,null=True, blank=True)
    last_service_date = models.DateField(null=True, blank=True)
    notificated = models.BooleanField()

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-id']
        db_table = 'notifications'