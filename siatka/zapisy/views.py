from django.db.models import Sum
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView, TemplateView, DetailView
from .models import Event, Player, Entry
from .forms import EntryForm

# Create your views here.

class AllEventsView(ListView):
    model = Event
    template_name = "zapisy/events.html"

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
            balance = player.excess - balance_ms - balance_nms - balance_serv*2
            players.append((player.name, balance))

        players.sort(key = lambda x: x[1])
        context['players'] = players
        return context

class NewEntryView(TemplateView):
    template_name = "zapisy/new_entry.html"

class PlayerDetailView(DetailView):
    template_name = "zapisy/player_detail.html"

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
