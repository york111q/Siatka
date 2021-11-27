import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'siatka.settings')
import django
django.setup()

from datetime import datetime
from ..models import Entry


def main_iteration_range(events, oldest_event):
    oldest_event = events[0]
    latest_event = events[events.count()-1]
    months_of_record = (latest_event.date.year - oldest_event.date.year) * 12 + latest_event.date.month - oldest_event.date.month
    return range(oldest_event.date.month, oldest_event.date.month + months_of_record + 1)


def count_date(i, oldest_event):
    years_passed = 0
    while True:
        if i > 12:
            i -= 12
            years_passed += 1
        else:
            break

    year = oldest_event.date.year + years_passed
    month = i
    return month, year


def total_cost_fees(events_this_month):
    total_cost = 0
    for event in events_this_month:
        total_cost += event.count_total_cost_fees()

    return total_cost


def total_paid_fees(events_this_month):
    total_cost = 0
    for event in events_this_month:
        total_cost += event.count_total_paid_fees()

    return total_cost


def total_cost_serves(events_this_month):
    total_cost = 0
    for event in events_this_month:
        total_cost += event.count_total_cost_serves()

    return total_cost


def total_paid_serves(events_this_month):
    total_cost = 0
    for event in events_this_month:
        total_cost += event.count_total_paid_serves()

    return total_cost


def total_for_site(events_this_month):
    total_cost = 0
    for event in events_this_month:
        total_cost += event.cost_for_site()

    return total_cost


def main(events):
    oldest_event = events[0]

    all_month_stats = []
    for i in main_iteration_range(events, oldest_event):
        month, year = count_date(i, oldest_event)

        events_this_month = events.filter(date__year=year, date__month=month)

        stats = {
                 'date': str(month) + '.' + str(year),
                 'number_of_events': events_this_month.count(),
                 'total_cost_fees': total_cost_fees(events_this_month),
                 'total_gathered_fees': total_paid_fees(events_this_month),
                 'total_cost_serves': total_cost_serves(events_this_month),
                 'total_gathered_serves': total_paid_serves(events_this_month),
                 'total_for_site': total_for_site(events_this_month),
                 'number_of_coaches': events_this_month.filter(coach=True).count(),
                 'total_for_coach': events_this_month.filter(coach=True).count() * 180,
        }

        all_month_stats.append(stats)

    return all_month_stats
