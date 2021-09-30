from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView, TemplateView, DetailView
from .models import Event, Player
from .forms import EntryForm

# Create your views here.

class AllEventsView(ListView):
    model = Event
    template_name = "zapisy/events.html"

class HallOfFameView(ListView):
    model = Player
    template_name = "zapisy/hof.html"

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
