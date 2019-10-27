from django import template
register = template.Library()

from apps.main.models import Mark
from apps.main.car_choices import *


def get_list(choice, name):
    result_list = list()
    for item in choice:
        result_list.append({
            'text': item[1],
            'value': f'value={item[0]}' if item[0] is not None else 'value',
            'selected': 'selected' if name == str(item[0]) else ''
        })
    return result_list


@register.simple_tag()
def gearbox(request):
    return get_list(GEARBOX_CHOICE, request.GET.get('gearbox'))


@register.simple_tag()
def cleared(request):
    return get_list(CLEARED_CHOISE, request.GET.get('cleared'))


@register.simple_tag()
def dtp(request):
    return get_list(DTP_CHOISE, request.GET.get('dtp'))


@register.simple_tag()
def location(request):
    return get_list(LOCATION_CHOICE, request.GET.get('location'))


@register.simple_tag()
def drive(request):
    return get_list(DRIVE_CHOICE, request.GET.get('drive'))


@register.simple_tag()
def body(request):
    return get_list(BODY_CHOICE, request.GET.get('body'))


@register.simple_tag()
def fuel(request):
    return get_list(FUEL_CHOICE, request.GET.get('fuel'))


@register.simple_tag(name='marks')
def mark_list():
    return Mark.objects.all()
