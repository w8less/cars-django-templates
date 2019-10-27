"""Multithreaded parsing and update utilities"""
from threading import Thread
from django.core.paginator import Paginator

from apps.main.models import Car
from apps.parsers.ab.parser import Ab

from celery import shared_task


@shared_task(time_limit=300)
def ab_parse():
    """Start parser"""
    ab_obj = Ab()
    count = 5
    threads = []
    for i in range(1, count + 1):
        finish = int(f'{i}01')
        start = finish - 100
        thread = Thread(target=ab_obj.parse, args=(start, finish))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()


@shared_task
def ab_update():
    """Start updater"""
    ab_obj = Ab()
    count = 5
    threads = []
    paginator = Paginator(Car.objects.filter(sold=False).exclude(ab_car_id=''), count)
    for page in range(1, paginator.num_pages):
        car_list = paginator.page(page)
        for car in car_list:
            thread = Thread(target=ab_obj.update, args=(car,))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
