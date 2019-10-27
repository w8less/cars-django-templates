import random
from django import template
register = template.Library()

from apps.main.models import FavouriteCar


@register.simple_tag()
def is_fav(request, car_id):
    return bool(FavouriteCar.objects.filter(car=car_id, user=request.user).exists())


@register.filter
def shuffle(arg):
    tmp = list(arg)[:5]
    random.shuffle(tmp)
    return tmp
