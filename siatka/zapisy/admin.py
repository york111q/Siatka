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
    list_editable = ['multisport', 'paid', 'serves', 'serves_paid']


class EntryInline(admin.TabularInline):
    model = Entry


class EventAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'location', 'price', 'price_multisport',
                    'player_slots', 'coach', 'cancelled', 'include_in_rank']
    ordering = ('-date',)
    list_filter = ['location', 'coach', 'cancelled']
    inlines = [EntryInline,]
    list_editable = ['include_in_rank']


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'player', 'value', 'done_by_python']
    ordering = ('created_at',)
    list_filter = ['player', 'done_by_python']
    date_hierarchy = 'created_at'


class PlayerAdmin(admin.ModelAdmin):
    list_display = ['name', 'multisport_number', 'count_balance']
    ordering = ('name',)
    list_editable = ['multisport_number']


class LocalizationAdmin(admin.ModelAdmin):
    list_display = ['address', 'image_file_name']
    ordering = ('address',)


class PlayerOldStatsAdmin(admin.ModelAdmin):
    list_display = ['player', 'bad_serves', 'events']
    ordering = ('player',)
    list_editable = ['bad_serves', 'events']


admin.site.register(Player, PlayerAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Entry, EntryAdmin)
admin.site.register(Localization, LocalizationAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(PlayerOldStats, PlayerOldStatsAdmin)
