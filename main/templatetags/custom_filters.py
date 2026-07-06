from django import template
from main.utils import get_severity_color, get_severity_icon, format_timestamp, truncate_text

register = template.Library()

@register.filter(name='severity_color')
def severity_color_filter(value):
    return get_severity_color(value)

@register.filter(name='severity_icon')
def severity_icon_filter(value):
    return get_severity_icon(value)

@register.filter(name='format_timestamp')
def format_timestamp_filter(value):
    if not value:
        return ""
    return format_timestamp(value)

@register.filter(name='truncate_text')
def truncate_text_filter(value, max_length=100):
    if not value:
        return ""
    try:
        length = int(max_length)
        return truncate_text(value, length)
    except ValueError:
        return truncate_text(value, 100)
