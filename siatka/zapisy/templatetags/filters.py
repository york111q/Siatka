from django import template
from django.utils.text import slugify
register = template.Library()

@register.filter
def nice_string(text):
    return "zapisy/images/"+slugify(text)+".jpg"