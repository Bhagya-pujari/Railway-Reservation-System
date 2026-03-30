from django.db import models
from django.contrib.auth.models import User


class Train(models.Model):
    TRAIN_TYPES = (
        ('AC', 'AC'),
        ('Sleeper', 'Sleeper'),
        ('General', 'General'),
    )
    train_number = models.CharField(max_length=20,default="TEMP123")
    
    name = models.CharField(max_length=100)
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_time = models.TimeField(default="00:00:00")
    arrival_time = models.TimeField(default="00:00:00")
    price = models.IntegerField(default=500) 
    coach_type = models.CharField(
    max_length=20,
    choices=[
        ('AC', 'AC'),
        ('Sleeper', 'Sleeper'),
        ('General', 'General')
    ],
    default='AC'   
)
    seats = models.IntegerField()

    def __str__(self):
        return f"{self.train_number} - {self.name}"


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    travel_date = models.DateField()

    def __str__(self):
        return f"{self.user.username} - {self.train.name}"