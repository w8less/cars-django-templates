from cars.celery import app

from apps.users.models import UserFilter, NewFilter
from apps.telegram.tasks import send_message


def get_car_cls():
    from main.models import Car
    return Car

NEW_CAR = """Новый автомобиль
{mark} {model} {year} года
${price}

Перейти на сайт:
{ab_link}
{ria_link}
"""

UPD_PRICE = """Обновлена цена
{mark} {model} {year} года
${price} (Старая цена - ${old_price})

Перейти на сайт:
{ab_link}
{ria_link}
"""


@app.task
def check_filters(car_id):
    car_qs = get_car_cls().objects.filter(id=car_id)
    filter_qs = UserFilter.objects.filter(is_active=True)
    for filter_obj in filter_qs:
        if car_qs.filter(**filter_obj.get_filtered_fields()):
            car_obj = car_qs.first()
            if car_obj.pricehistory_set.count() > 1:
                text_message = UPD_PRICE
                old_price = car_obj.pricehistory_set.all().order_by('-id')[1].price
            else:
                text_message = NEW_CAR
                old_price = None
            formatted_text = text_message.format(
                mark=car_obj.model.mark,
                model=car_obj.model,
                year=car_obj.year,
                price=car_obj.price,
                old_price=old_price,
                ab_link=car_obj.ab_link,
                ria_link=car_obj.ria_link
            )
            send_message.delay(filter_obj.user.telegram_id, text=formatted_text, parse_mode=None)


# @app.task
# def check_filters(car_id):
#     car_qs = get_car_cls().objects.filter(id=car_id)
#     filter_qs = NewFilter.objects.filter(is_active=True)
#     for filter_obj in filter_qs:
#         if car_qs.filter(**filter_obj.get_filtered_fields()):
#             car_obj = car_qs.first()
#             if car_obj.pricehistory_set.count() > 1:
#                 text_message = UPD_PRICE
#                 old_price = car_obj.pricehistory_set.all().order_by('-id')[1].price
#             else:
#                 text_message = NEW_CAR
#                 old_price = None
#             formatted_text = text_message.format(
#                 mark=car_obj.model.mark,
#                 model=car_obj.model,
#                 year=car_obj.year,
#                 price=car_obj.price,
#                 old_price=old_price,
#                 ab_link=car_obj.ab_link,
#                 ria_link=car_obj.ria_link
#             )
#             send_message.delay(filter_obj.user.telegram_id, text=formatted_text, parse_mode=None)
