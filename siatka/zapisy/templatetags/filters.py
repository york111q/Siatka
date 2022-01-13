from django import template
from django.utils.safestring import mark_safe
register = template.Library()


@register.filter
def show_date(date):
    return date.strftime('%Y-%m-%d %H:%M')

@register.filter
def show_price(value):
    return str("{:.2f}".format(value)).replace(".", ",") + 'zł'

@register.filter
def show_colored_price(value):
    value_str = show_price(value)
    if value > 0:
        return mark_safe(f'<span class="text-success">{value_str}</span>')
    elif value < 0:
        return mark_safe(f'<span class="text-danger">{value_str}</span>')
    else:
        return mark_safe(f'<span class="text-warning">{value_str}</span>')

@register.filter(is_safe=True)
def bool_symbol(bool):
    if bool:
        return mark_safe('<i class="bi bi-check-circle text-success"></i>')
    else:
        return mark_safe('<i class="bi bi-x-circle text-danger"></i>')
