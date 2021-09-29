from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('events/', views.AllEventsView.as_view(), name='events')
]
