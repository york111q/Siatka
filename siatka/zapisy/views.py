from django.shortcuts import render
from django.views.generic import ListView
from .models import Event

# Create your views here.

class AllEventsView(ListView):
    model = Event
    template_name = "zapisy/events.html"
