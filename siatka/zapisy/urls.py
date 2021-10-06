from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.AllEventsView.as_view(), name='events'),
    path('hall-of-fame/', views.HallOfFameView.as_view(), name='hof'),
    path('new-entry/<int:id>', views.new_entry, name='new_entry'),
    path('player/<int:pk>', views.PlayerDetailView.as_view(), name='player'),
    path('event/<int:id>', views.EventDetailView.as_view(), name='event'),
]

if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
