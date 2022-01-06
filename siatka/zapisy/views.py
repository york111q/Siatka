from datetime import datetime, timezone
from django.conf import settings
from django.db.models import Sum, Count, Case, When, Value, IntegerField, Q, F, ExpressionWrapper, FloatField
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, TemplateView, DetailView, FormView, DeleteView, UpdateView
from .models import Event, Player, Entry, Payment, PlayerOldStats
from .forms import EntryForm, EventManagerForm
from .utils import summary_maker
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
        context['ended'] = events.filter(date__lte=datetime.now(), cancelled=False).order_by('-date')
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

        context['player_payments'] = Payment.objects.filter(player=player)

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

        return render(request, self.template_name, context)


class PlayerFormView(FormView):
    form_class = EntryForm
    template_name = 'zapisy/success.html'
    success_url = '/'

    def post(self, request, *args, **kwargs):
        playerform = self.form_class(request.POST)
        adminform = EventManagerForm()
        if playerform.is_valid():
            cd = playerform.cleaned_data
            event = Event.objects.get(id=kwargs['id'])
            player_entries = Entry.objects.filter(event=event, reserve=False)

            if cd['player'].multisport_number is not None:
                cd['multisport'] = True

            if player_entries.count() < event.player_slots:
                Entry.objects.update_or_create(event=event, player=cd['player'], defaults=cd)
                return self.render_to_response(self.get_context_data(success=True))
            else:
                Entry.objects.update_or_create(event=event, reserve=True, player=cd['player'], defaults=cd)
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
                    cd = adminform.cleaned_data
                    player_entries = Entry.objects.filter(event=event, reserve=False)

                    if player_entries.filter(player=cd['player']).count() == 0:
                        if cd['player'].multisport_number is not None:
                            cd['multisport'] = True

                    Entry.objects.update_or_create(event=event, player=cd['player'], defaults=cd)

                    if player_entries.count() > event.player_slots:
                        entry = Entry.objects.get(event=event, player=cd['player'], defaults=cd)
                        entry.reserve = True
                        return self.render_to_response(self.get_context_data(success=False))

        return self.render_to_response(self.get_context_data(success=True, event=event.id))


class ServeRank(TemplateView):
    template_name = 'zapisy/serve_rank.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        events_attended = Count(Case(
            When(
                Q(entry__event__date__lt=datetime.now()) &
                Q(entry__event__include_in_rank=True),
                then=1
            ),
            output_field = IntegerField()),
            default = Value(0))

        old_events = Case(
            When(playeroldstats__bad_serves__gte=0, then='playeroldstats__events'),
            default=Value(0))

        current_serves = Sum(Case(
            When(entry__event__include_in_rank=True, then='entry__serves'),
            default=Value(0)))

        old_serves = Case(
            When(playeroldstats__bad_serves__gte=0, then='playeroldstats__bad_serves'),
            default=Value(0))

        serve = current_serves + old_serves
        events = events_attended + old_events

        annotated_players = Player.objects.all().annotate(
            serve = serve,
            events = events,
            ratio = ExpressionWrapper(
                1.0 * serve / events,
                output_field = FloatField()
                )
            )

        player_queryset = annotated_players.filter(events__gte=5)
        listed_players = list(set(player_queryset))
        listed_players.sort(key=lambda x:-x.ratio)

        context['players'] = listed_players
        context['title'] = "Ranking zagrywek"
        context['year'] = datetime.now().year

        return context


class ServeYearRank(TemplateView):
    template_name = 'zapisy/serve_year_rank.html'

    def get(self, request, year, *args, **kwargs):
        context = self.get_context_data()
        context['year'] = year
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        years = []

        # Stats 2021 - before page started
        all_stats = PlayerOldStats.objects.all()

        year_stats = (2021, [])
        for stat in all_stats:
            if stat.events > 5:
                year_stats[-1].append({
                    'name': stat.player.name,
                    'serve': stat.bad_serves,
                    'events': stat.events,
                    'ratio': stat.bad_serves / stat.events
                })

        years = [year_stats]

        # Stats 2022+ after page started
        all_players = Player.objects.all()

        for i in range(2022, 2099):
            year_events = Event.objects.filter(date__year=i, include_in_rank=True)
            if year_events.count() == 0:
                break

            years.append((i, []))

            for player in all_players:
                entries = Entry.objects.filter(event__in=year_events, player=player)

                serves = 0
                for entry in entries:
                    serves += entry.serves

                events = entries.count()

                if events >= 5:
                    years[-1][-1].append({
                        'name': player.name,
                        'serve': serves,
                        'events': events,
                        'ratio': 1.0 * serves / events
                    })

        context['years'] = years
        context['title'] = f'Ranking za rok '

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

        event = Event.objects.get(id=self.kwargs['pk'])
        context['event'] = event

        all_event_entries = Entry.objects.filter(event=event, reserve=False)
        all_unpaid = all_event_entries.filter(Q(paid=False) | Q(serves_paid=False))

        all_unpaid_to_pay = [entry for entry in all_unpaid if entry.player.count_balance() >= 0 or entry.count_total_fee() == 0]

        context['all_unpaid_to_pay'] = all_unpaid_to_pay

        return context

    def post(self, *args, **kwargs):

        context = self.get_context_data()
        all_unpaid_to_pay = context['all_unpaid_to_pay']

        def update_payments(entry):
            entry.paid = True
            entry.serves_paid = True
            entry.save()
            return True

        for entry in all_unpaid_to_pay:
            if entry.count_entry_fee() > 0:
                Payment.objects.create(player=entry.player, value=-entry.count_entry_fee())

            if entry.count_serves_fee() > 0:
                Payment.objects.create(player=entry.player, value=-entry.count_serves_fee())

            update_payments(entry)

        return HttpResponseRedirect(f'/event/{self.kwargs["pk"]}')


class EventPay0ConfirmView(TemplateView):
    template_name = 'zapisy/pay_from_excess_confirm.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        event = Event.objects.get(id=self.kwargs['pk'])
        context['event'] = event

        all_event_entries = Entry.objects.filter(event=event, reserve=False)
        all_unpaid = all_event_entries.filter(Q(paid=False) | Q(serves_paid=False))

        all_unpaid_fee = [entry for entry in all_unpaid if entry.count_entry_fee() == 0 and entry.paid == False]
        all_unpaid_serves = [entry for entry in all_unpaid if entry.count_serves_fee() == 0 and entry.serves_paid == False]

        context['all_unpaid_fee'] = all_unpaid_fee
        context['all_unpaid_serves'] = all_unpaid_serves

        return context

    def post(self, *args, **kwargs):

        context = self.get_context_data()
        all_unpaid_to_pay = context['all_unpaid_fee'] + context['all_unpaid_serves']

        for entry in all_unpaid_to_pay:
            if entry.count_entry_fee() == 0:
                entry.paid = True
                entry.save()

            if entry.count_serves_fee() == 0:
                entry.serves_paid = True
                entry.save()

        return HttpResponseRedirect(f'/event/{self.kwargs["pk"]}')


class MonthlySummary(TemplateView):
    template_name = 'zapisy/monthly_summary.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['try'] = summary_maker.main(Event.objects.order_by('date'))

        return context
