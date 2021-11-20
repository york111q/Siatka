from datetime import datetime, timezone
from django.conf import settings
from django.db.models import Sum, Count, Case, When, IntegerField, Q, F, ExpressionWrapper, FloatField
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, TemplateView, DetailView, FormView, DeleteView, UpdateView
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
        #events = Event.objects.annotate(num_signed=Count('entry'))
        events = Event.objects.annotate(num_signed=Count(Case(When(entry__reserve=False, then=1), output_field=IntegerField())),
                                        num_reserve=Count(Case(When(entry__reserve=True, then=1), output_field=IntegerField())),
                                        num_paid=Count(Case(When(Q(entry__paid=True) & Q(entry__serves_paid=True), then=1), output_field=IntegerField())))
        context['upcoming'] = events.filter(date__gte=datetime.now())
        context['ended'] = events.filter(date__lte=datetime.now())
        return context


class HallOfFameView(ListView):
    model = Player
    template_name = "zapisy/hof.html"

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)

        all_players = Player.objects.all()

        check_player_balances = map(lambda player:(player, player.count_balance()), all_players)
        player_list = list(check_player_balances)
        player_list.sort(key = lambda x: x[1])

        context['player_list'] = player_list
        return context


class PlayerDetailView(DetailView):
    template_name = "zapisy/player_detail.html"
    queryset = Player.objects.all()
    related_name = 'player'

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)

        player = Player.objects.get(id=self.kwargs['pk'])
        attended_entries = Entry.objects.filter(player=player, reserve=False)
        entries_unpaid = attended_entries.filter(Q(paid=False) | Q(serves_paid=False))

        context['entries_unpaid'] = entries_unpaid.order_by('-event__date')
        context['all_entries'] = attended_entries.order_by('-event__date')

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
                adminformlist.append(EventManagerForm(self.request.GET or None, prefix=str(i), initial=data))
            except:
                adminformlist.append(EventManagerForm(self.request.GET or None, prefix=str(i)))

        context['adminforms'] = adminformlist
        context['event_id'] = kwargs['pk']
        context['ended'] = event.date < datetime.now()
        context['event'] = event
        context['player_entries'] = Entry.objects.filter(event=event, reserve=False)
        context['player_reserve'] = Entry.objects.filter(event=event, reserve=True)

        #return self.render_to_response(context) -- render to response nie działa w django 3+ ?
        return render(request, self.template_name, context)

class PlayerFormView(FormView):
    form_class = EntryForm
    template_name = 'zapisy/success.html'
    success_url = '/'

    def post(self, request, *args, **kwargs):
        playerform = self.form_class(request.POST)
        adminform = EventManagerForm()
        if playerform.is_valid():
            event = Event.objects.get(id=kwargs['id'])
            player_entries = Entry.objects.filter(event=event, reserve=False)
            if player_entries.count() < event.player_slots:
                Entry.objects.update_or_create(event=event, player=playerform.cleaned_data['player'], defaults=playerform.cleaned_data)
                return self.render_to_response(self.get_context_data(success=True))
            else:
                Entry.objects.update_or_create(event=event, reserve=True, player=playerform.cleaned_data['player'], defaults=playerform.cleaned_data)
                return self.render_to_response(self.get_context_data(success=False))
        else:
            return self.render_to_response(self.get_context_data(playerform=playerform))

class AdminFormView(FormView):
    form_class = EventManagerForm
    template_name = 'zapisy/success.html'
    success_url = '/'

    def post(self, request, *args, **kwargs):
        playerform = EventManagerForm()

        event = Event.objects.get(id=kwargs['id'])
        forms = []
        for i in range(event.player_slots):
            forms.append(self.form_class(self.request.POST, prefix=str(i)))

        for adminform in forms:
            if adminform.is_valid():
                if adminform.cleaned_data['player']:
                    player_entries = Entry.objects.filter(event=event, reserve=False)
                    Entry.objects.update_or_create(event=event, player=adminform.cleaned_data['player'], defaults=adminform.cleaned_data)
                    if player_entries.count() > event.player_slots:
                        entry = Entry.objects.get(event=event, player=adminform.cleaned_data['player'], defaults=adminform.cleaned_data)
                        entry.reserve = True
                        return self.render_to_response(self.get_context_data(success=False))

        return self.render_to_response(self.get_context_data(success=True))


'''def new_entry(request, id):
    form = EntryForm()

    if request.method == "POST":
        form = EntryForm(request.POST)

        if form.is_valid():
            entry = form.save(commit=False)
            entry.event = Event.objects.get(id=id)
            entry.save()
            return redirect(reverse('events'))

    return render(request, 'zapisy/new_entry.html', {'form': form})'''


class ServeRank(TemplateView):
    template_name = 'zapisy/serve_rank.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        all_players = Player.objects.all()

        total_bad_serves = Sum('entry__serves')
        events_attended = Count('entry')

        annotated_players = all_players.annotate(serve=total_bad_serves,
                                                 events=events_attended,
                                                 ratio=ExpressionWrapper(1.0*total_bad_serves/events_attended, output_field=FloatField()))

        context['players'] = annotated_players.order_by('-ratio')

        return context


class PlayersList(ListView):
    model = Player


class EntryDeleteView(DeleteView):
    model = Entry
    success_url = reverse_lazy("events")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        ## ADDED
        event_reserves = self.object.event.entry_set.filter(reserve=True)
        if event_reserves.count() > 0:
            first_reserve = event_reserves.order_by('created_at')[0]
            first_reserve.reserve = False
            first_reserve.save()
        ##
        self.object.delete()
        return HttpResponseRedirect(success_url)


class EventCancelView(UpdateView):
    template_name = 'zapisy/event_confirm_cancel.html'
    model = Event
    fields = ('cancelled',)

    def post(self, *args, **kwargs):
        object = Event.objects.get(id=self.kwargs['pk'])
        object.cancelled = True
        object.save()

        entries_to_delete = Entry.objects.filter(event=object)
        for entry in entries_to_delete:
            entry.delete()

        return HttpResponseRedirect(f'/event/{self.kwargs["pk"]}')


class EventPayConfirmView(TemplateView):
    template_name = "zapisy/pay_from_excess_confirm.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['event'] = Event.objects.get(id=self.kwargs['pk'])

        all_event_entries = Entry.objects.filter(event=context['event'])
        context['all_unpaid'] = Entry.objects.filter(paid=False)
        context['all_unpaid_serves'] = Entry.objects.filter(serves_paid=False)

        return context
