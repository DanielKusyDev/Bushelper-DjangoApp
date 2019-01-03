from django.template import Library
register = Library()


@register.simple_tag
def define(val=None):
    return val