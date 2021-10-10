from datetime import datetime, timezone
from django.conf import settings
from django.db.models import Sum
from django.forms.models import model_to_dict
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView, TemplateView, DetailView, FormView
from .models import Event, Player, Entry
from .forms import EntryForm, EventManagerForm
import pytz

# Create your views here.
SERVE_PRICE = 2

class AllEventsView(ListView):
    model = Event
    template_name = "zapisy/events.html"

    def get_context_data(self, **kwargs):
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
        all_entries = Entry.objects.filter(player=player).order_by('-event__date')

        entries_unpaid_list = []
        #for entry in all_unpaid:
        for entry in all_entries:
            payment = 0
            if not entry.paid:
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

class EventDetailView(TemplateView):
    template_name = 'zapisy/event_detail.html'

    def get(self, request, *args, **kwargs):
        playerform = EntryForm(self.request.GET or None)
        adminform = EventManagerForm(self.request.GET or None)

        context = self.get_context_data(**kwargs)
        context['playerform'] = playerform

        event = Event.objects.get(id=kwargs['pk'])
        event_entries = Entry.objects.filter(event=event)

        adminformlist = []
        for i in range(event.player_slots):
            try:
                data = model_to_dict(event_entries[i], fields=['player', 'multisport', 'serves', 'paid', 'serves_paid', 'resign'])
                print(data)
                adminformlist.append(EventManagerForm(self.request.GET or None, prefix=str(i), initial=data))
            except:
                adminformlist.append(EventManagerForm(self.request.GET or None, prefix=str(i)))

        context['adminforms'] = adminformlist
        context['event_id'] = kwargs['pk']
        context['ended'] = event.date < datetime.now()
        context['event'] = event

        return self.render_to_response(context)

class PlayerFormView(FormView):
    form_class = EntryForm
    template_name = 'zapisy/success.html'
    success_url = '/'

    def post(self, request, *args, **kwargs):
        playerform = self.form_class(request.POST)
        adminform = EventManagerForm()
        if playerform.is_valid():
            Entry.objects.update_or_create(event=Event.objects.get(id=kwargs['id']), player=playerform.cleaned_data['player'], defaults=playerform.cleaned_data)

            return self.render_to_response(self.get_context_data(success=True))
        else:
            return self.render_to_response(self.get_context_data(playerform=playerform))

class AdminFormView(FormView):
    form_class = EventManagerForm
    template_name = 'zapisy/success.html'
    success_url = '/'

    def post(self, request, *args, **kwargs):
        playerform = EventManagerForm()

        forms = []
        for i in range(Event.objects.get(id=kwargs['id']).player_slots):
            forms.append(self.form_class(self.request.POST, prefix=str(i)))

        for adminform in forms:
            if adminform.is_valid():
                if adminform.cleaned_data['player']:
                    Entry.objects.update_or_create(event=Event.objects.get(id=kwargs['id']), player=adminform.cleaned_data['player'], defaults=adminform.cleaned_data)

        return self.render_to_response(self.get_context_data(success=True))


def new_entry(request, id):
    form = EntryForm()

    if request.method == "POST":
        form = EntryForm(request.POST)

        if form.is_valid():
            entry = form.save(commit=False)
            entry.event = Event.objects.get(id=id)
            entry.save()
            return redirect(reverse('events'))

    return render(request, 'zapisy/new_entry.html', {'form': form})
