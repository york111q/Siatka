from datetime import datetime
from django.conf import settings
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView, TemplateView, DetailView
from .models import Event, Player, Entry
from .forms import EntryForm

# Create your views here.
SERVE_PRICE = 2

class AllEventsView(ListView):
    model = Event
    template_name = "zapisy/events.html"

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['upcoming'] = Event.objects.filter(date__gte=datetime.now())
        context['ended'] = Event.objects.filter(date__lte=datetime.now())
        return context

class HallOfFameView(ListView):
    model = Player
    template_name = "zapisy/hof.html"

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)

        player_objects = Player.objects.all()
        players = []

        for player in player_objects:
            entries = Entry.objects.filter(player=player).filter(paid=False)
            balance_ms = entries.filter(multisport=False).aggregate(n=Sum('event__price'))['n'] or 0
            balance_nms = entries.filter(multisport=True).aggregate(n=Sum('event__price_multisport'))['n'] or 0
            entries = Entry.objects.filter(player=player).filter(serves_paid=False)
            balance_serv = entries.aggregate(n=Sum('serves'))['n'] or 0
            balance = player.excess - balance_ms - balance_nms - balance_serv * SERVE_PRICE

            players.append({'name': player.name,
                            'balance': balance,
                            'id':player.id})

        players.sort(key = lambda x: x['balance'])
        context['players'] = players
        return context

class NewEntryView(TemplateView):
    template_name = "zapisy/new_entry.html"

class PlayerDetailView(DetailView):
    template_name = "zapisy/player_detail.html"
    queryset = Player.objects.all()
    related_name = 'player'

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)

        player = Player.objects.get(id=self.kwargs['pk'])

        entries_unpaid = Entry.objects.filter(player=player).filter(paid=False)
        balance_ms = entries_unpaid.filter(multisport=False).aggregate(n=Sum('event__price'))['n'] or 0
        balance_nms = entries_unpaid.filter(multisport=True).aggregate(n=Sum('event__price_multisport'))['n'] or 0
        entries_unpaid_serves = Entry.objects.filter(player=player).filter(serves_paid=False)
        balance_serv = entries_unpaid_serves.aggregate(n=Sum('serves'))['n'] or 0
        balance = player.excess - balance_ms - balance_nms - balance_serv * SERVE_PRICE

        context['name'] = player.name
        context['balance'] = balance

        all_unpaid = (entries_unpaid | entries_unpaid_serves).order_by('-event__date')

        entries_unpaid_list = []
        for entry in all_unpaid:
            payment = 0
            if entry.paid:
                if entry.multisport:
                    payment += entry.event.price_multisport
                else:
                    payment += entry.event.price

            if not entry.serves_paid and entry.serves > 0:
                payment += entry.serves * 2

            entries_unpaid_list.append({'date': entry.event.date.strftime('%Y-%m-%d %H:%M'),
                                       'location': entry.event.location,
                                       'multisport': entry.multisport,
                                       'serves': entry.serves,
                                       'serves_paid': entry.serves_paid,
                                       'paid': entry.paid,
                                       'resign': entry.resign,
                                       'payment': payment})

        context['entries_unpaid'] = all_unpaid
        context['entries_unpaid_list'] = entries_unpaid_list

        context['all_entries'] = Entry.objects.filter(player=player).order_by('-event__date')

        return context

class EventDetailView(DetailView):
    template_name = "zapisy/event_detail.html"


def new_entry(request, id):
    form = EntryForm()

    if request.method == "POST":
        form = EntryForm(request.POST)

        if form.is_valid():
            entry = form.save(commit=False)
            entry.event = Event.objects.get(id=id)
            entry.save()
            return redirect(reverse('events'))
    #    else:
    #        return

    return render(request, 'zapisy/new_entry.html', {'form': form})
