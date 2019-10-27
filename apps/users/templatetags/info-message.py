from django import template
register = template.Library()

from apps.users.models import InfoMessage


@register.simple_tag()
def info_message():
    return InfoMessage.objects.first().message if InfoMessage.objects.first() else ''
