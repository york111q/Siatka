from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.AllEventsView.as_view(), name='events'),
    path('hall-of-fame/', views.HallOfFameView.as_view(), name='hof'),
    path('player-list/', views.PlayersList.as_view(), name='player_list'),
    path('serve-rank/', views.ServeRank.as_view(), name='serve_rank'),
    path('new-entry/<int:id>', views.new_entry, name='new_entry'),
    path('entry/delete/<int:pk>', views.EntryDeleteView.as_view(), name='entry_delete'),
    path('player/<int:pk>', views.PlayerDetailView.as_view(), name='player'),
    path('event/<int:pk>', views.EventDetailView.as_view(), name='event'),
    path('event/<int:id>/playerform', views.PlayerFormView.as_view(), name='playerform'),
    path('event/<int:id>/adminform', views.AdminFormView.as_view(), name='adminform'),
]

if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
