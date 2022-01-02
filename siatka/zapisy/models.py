from django.db import models
from django.db.models import Sum
from django.urls import reverse
import datetime


# Create your models here.

class Player(models.Model):
    name = models.CharField(max_length=64)
    multisport_number = models.CharField(max_length=8, null=True, blank=True)

    def count_balance(self):
        player_entries = Entry.objects.filter(player=self, reserve=False)
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

    def count_normal_cost_fees(self):
        normal_entries = Entry.objects.filter(event=self, multisport=False).count()
        return normal_entries * self.price

    def count_ms_cost_fees(self):
        ms_entries = Entry.objects.filter(event=self, multisport=True).count()
        return ms_entries * self.price_multisport

    def count_total_cost_fees(self):
        return self.count_normal_cost_fees() + self.count_ms_cost_fees()

    def count_normal_paid_fees(self):
        normal_entries = Entry.objects.filter(event=self, multisport=False, paid=True).count()
        return normal_entries * self.price

    def count_ms_paid_fees(self):
        ms_entries = Entry.objects.filter(event=self, multisport=True, paid=True).count()
        return ms_entries * self.price_multisport

    def count_total_paid_fees(self):
        return self.count_normal_paid_fees() + self.count_ms_paid_fees()

    def count_total_cost_serves(self):
        event_entries = Entry.objects.filter(event=self).aggregate(Sum('serves'))
        if event_entries['serves__sum']:
            return event_entries['serves__sum'] * 2
        else:
            return 0

    def count_total_paid_serves(self):
        event_entries = Entry.objects.filter(event=self, serves_paid=True).aggregate(Sum('serves'))
        if event_entries['serves__sum']:
            return event_entries['serves__sum'] * 2
        else:
            return 0

    def cost_for_site(self):
        no_ms_players = Entry.objects.filter(event=self, multisport=False).count()
        cost = self.price * (10 - no_ms_players)
        if cost < 0:
            cost = 0
        return cost

    def __str__(self):
        return self.date.strftime('%Y-%m-%d %H:%M %A')


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
        if not self.paid:
            if self.multisport:
                return self.event.price_multisport
            else:
                return self.event.price
        else:
            return 0

    def count_serves_fee(self):
        if not self.serves_paid:
            return self.serves * 2
        else:
            return 0

    def count_total_fee(self):
        return self.count_entry_fee() + self.count_serves_fee()

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


class PlayerOldStats(models.Model):
    player = models.OneToOneField("Player", on_delete=models.CASCADE)
    events = models.PositiveIntegerField()
    bad_serves = models.PositiveIntegerField()

    def __str__(self):
        return self.player.name
