from django.utils import timezone

from apps.main.models import PriceHistory


def set_price(price, car):
    if price:
        PriceHistory(car=car, price=price, date_set=timezone.now(), site='OLX').save()
