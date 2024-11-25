# app/templatetags/app_extras.py
from django import template
import base64

register = template.Library()

@register.filter
def b64encode(value):
    return base64.b64encode(value).decode('utf-8')

@register.filter
def to(value, arg):
    return range(value, arg+1)

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
