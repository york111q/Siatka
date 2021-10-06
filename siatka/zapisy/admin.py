from django.contrib import admin
from .models import Player, Event, Entry, Localization

# Register your models here.
admin.site.register(Player)
admin.site.register(Event)
admin.site.register(Entry)
admin.site.register(Localization)
