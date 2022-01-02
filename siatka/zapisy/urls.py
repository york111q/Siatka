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
    path('monthly-summary/', views.MonthlySummary.as_view(), name='monthly_summary'),
    path('entry/delete/<int:pk>', views.EntryDeleteView.as_view(), name='entry_delete'),
    path('player/<int:pk>', views.PlayerDetailView.as_view(), name='player'),
    path('event/<int:pk>', views.EventDetailView.as_view(), name='event'),
    path('event/<int:id>/playerform', views.PlayerFormView.as_view(), name='playerform'),
    path('event/<int:id>/adminform', views.AdminFormView.as_view(), name='adminform'),
    path('event/<int:pk>/cancel', views.EventCancelView.as_view(), name='event_cancel'),
    path('event/<int:pk>/pay', views.EventPayConfirmView.as_view(), name='pay_from_excess_confirm'),
    path('event/<int:pk>/pay_0', views.EventPay0ConfirmView.as_view(), name='pay_zeros'),
]

if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
