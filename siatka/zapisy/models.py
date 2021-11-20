from django.db import models
from django.urls import reverse
import datetime

# Create your models here.

class Player(models.Model):
    name = models.CharField(max_length=64)
    multisport_number = models.CharField(max_length=8, null=True, blank=True)

    def count_balance(self):
        player_entries = Entry.objects.filter(player=self)
        player_payments = Payment.objects.filter(player=self)

        balance = 0

        for entry in player_entries:
            balance -= entry.count_total_fee()

        for payment in player_payments:
            balance += payment.value

        return balance

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
    cancelled = models.BooleanField(default=False)

    def __str__(self):
        return self.date.strftime('%Y-%m-%d %H:%M %A') + " " + self.location.address

class Entry(models.Model):
    event = models.ForeignKey("Event", on_delete=models.CASCADE)
    player = models.ForeignKey("Player", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    reserve = models.BooleanField(default=False)
    multisport = models.BooleanField(default=False)
    serves = models.IntegerField(default=0)
    paid = models.BooleanField(default=False)
    serves_paid = models.BooleanField(default=False)
    resign = models.BooleanField(default=False)

    def count_entry_fee(self):
        if self.multisport:
            return self.event.price_multisport
        else:
            return self.event.price

    def count_total_fee(self):
        return self.count_entry_fee() + self.serves * 2

    def __str__(self):
        return str(self.event) + " | " + str(self.player)

class Localization(models.Model):
    address = models.CharField(max_length=32)
    image = models.ImageField(upload_to='localizations')

    def __str__(self):
        return self.address

class Payment(models.Model):
    player = models.ForeignKey("Player", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    value = models.FloatField()
    done_by_python = models.BooleanField(default=True)

    def __str__(self):
        date = self.created_at.strftime("%Y-%m-%d %H:%M")
        show_value = str(round(self.value, 2)) + "zł"
        return date + " | " + self.player.name + " | " + show_value
