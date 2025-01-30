from django import template

register = template.Library()

@register.filter
def format_count(value):
    try:
        value = int(value)
        if value >= 1000:
            return f"{value/1000:.1f}k"
        return str(value)
    except (ValueError, TypeError):
        return "0"  # Return default value if conversion fails 