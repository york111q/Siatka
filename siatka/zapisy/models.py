from django.db import models
import datetime

# Create your models here.

class Player(models.Model):
    name = models.CharField(max_length=64)
    multisport_number = models.CharField(max_length=8, null=True, blank=True)
    excess = models.FloatField(default=0)

    def __str__(self):
        return self.name


class Event(models.Model):
    date = models.DateTimeField()
    duration = models.DurationField()
    location = models.ForeignKey("Localization", on_delete=models.SET_NULL, blank=True, null=True, default=None)
    price = models.FloatField()
    price_multisport = models.FloatField(default=0)
    player_slots = models.IntegerField(default=12)
    coach = models.BooleanField(default=False)

    def __str__(self):
        return self.date.strftime('%Y-%m-%d %H:%M %A') + " " + self.location.address

class Entry(models.Model):
    event = models.ForeignKey("Event", on_delete=models.CASCADE)
    player = models.ForeignKey("Player", on_delete=models.CASCADE)
    multisport = models.BooleanField(default=False)
    serves = models.IntegerField(default=0)
    paid = models.BooleanField(default=False)
    serves_paid = models.BooleanField(default=False)
    resign = models.BooleanField(default=False)

    def __str__(self):
        return str(self.event) + " | " + str(self.player)

class Localization(models.Model):
    address = models.CharField(max_length=32)
    image = models.ImageField(upload_to='localizations')

    def __str__(self):
        return self.address
