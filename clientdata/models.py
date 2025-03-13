from django.db import models
# Create your models here.

class Client(models.Model):
    name = models.CharField(max_length=100, blank=False, null=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'clients'
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ['-id']





class Car(models.Model):
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    color = models.CharField(max_length=50)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='cars')
    license_plate = models.CharField(max_length=20)
    last_service_date = models.DateField(null=True, blank=True)
    kms = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.brand} {self.model}"
    
    class Meta:
        db_table = 'cars'
        verbose_name = "Car"
        verbose_name_plural = "Cars"
        ordering = ['-id']



class CarHistory(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    service = models.ForeignKey('projects.Project', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.car}"
    
    class Meta:
        db_table = 'car_history'
        verbose_name = "Car History"
        verbose_name_plural = "Car Histories"
        ordering = ['-id']