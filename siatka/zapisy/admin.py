from django.contrib import admin
from .models import Player, Event, Entry, Localization, Payment, PlayerOldStats

# Register your models here.
class EntryAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at',)
    list_display = ['event', 'player', 'multisport', 'reserve', 'paid',
                    'serves', 'serves_paid', 'created_at']
    ordering = ('-event', '-created_at')
    date_hierarchy = 'created_at'
    list_filter = ['event', 'player']


class EntryInline(admin.TabularInline):
    model = Entry


class EventAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'location', 'price', 'price_multisport',
                    'player_slots', 'coach', 'cancelled']
    ordering = ('-date',)
    list_filter = ['location', 'coach', 'cancelled']
    inlines = [EntryInline,]


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'player', 'value', 'done_by_python']
    ordering = ('created_at',)
    list_filter = ['player', 'done_by_python']
    date_hierarchy = 'created_at'


class PlayerAdmin(admin.ModelAdmin):
    list_display = ['name', 'multisport_number', 'count_balance']
    ordering = ('name',)


admin.site.register(Player, PlayerAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Entry, EntryAdmin)
admin.site.register(Localization)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(PlayerOldStats)
