from django.contrib import admin
from .models import Player, Event, Entry, Localization, Payment

# Register your models here.
class EntryAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at',)


admin.site.register(Player)
admin.site.register(Event)
admin.site.register(Entry, EntryAdmin)
admin.site.register(Localization)
admin.site.register(Payment)
