from django import template
from django.utils.text import slugify
register = template.Library()

@register.filter
def img_url(text):
    return "zapisy/images/"+slugify(text)+".jpg"

@register.filter
def show_date(date):
    return date.strftime('%Y-%m-%d %H:%M')

@register.filter
def multiply(value, multiplier):
    return value*multiplier

@register.filter
def count_ratio(serves, events):
    if serves and events:
        return round(serves/events, 2)
    else:
        return 0
