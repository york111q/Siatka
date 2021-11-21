from django import template
from django.utils.safestring import mark_safe
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
def show_price(value):
    return str("{:.2f}".format(value)).replace(".", ",") + 'zł'

@register.filter
def entry_count_fee(object):
    return str("{:.2f}".format(object.count_total_fee())).replace(".", ",") + 'zł'

@register.filter
def check_balance(object):
    return object.count_balance()

@register.filter(is_safe=True)
def bool_symbol(bool):
    if bool:
        return mark_safe('<i class="bi bi-check-circle text-success"></i>')
    else:
        return mark_safe('<i class="bi bi-x-circle text-danger"></i>')
