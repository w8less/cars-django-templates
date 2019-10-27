"""Parser Autobazar (https://ab.ua/)"""
import json
import re
from datetime import datetime
import requests
from django.db.models import Q
from django.utils.timezone import get_current_timezone, now


from apps.parsers.utils import get_model_id, find_same_car

from apps.main.models import (
    Seller,
    Car,
    CarImage,
    CarLink,
    Location,
    PriceHistory,
    SellerPhone
)
from apps.parsers.choises import GEARBOX, FUEL, BODY, LOCATION

TZ = get_current_timezone()


def parse_data(json_data):

    def get_formatted_phone(phone):
        """Returns formatted phone number"""
        phone = re.sub(r'\D', '', phone)
        if len(phone) != 12:
            phone = '380' + phone[-9:]
        return phone

    def get_car_id():
        return json_data['id']

    def get_drive():
        if 'drive' in json_data['characteristics']:
            drive_id = json_data['characteristics']['drive']['id']
        elif json_data['drive']['slug']:
            drive_id = json_data['drive']['id']
        else:
            drive_id = None
        drives = {56: 1, 25: 2, 114: 3, 574: 3}
        return drives.get(drive_id)

    def get_gearbox():
        if 'gearbox' in json_data['characteristics'] and json_data['characteristics']['gearbox']['title']:
            gearbox = 1 if json_data['characteristics']['gearbox']['id'] == 82 else 2
        else:
            gearbox = None
        return gearbox

    def get_body():
        body = json_data['characteristics']['category']['title'].lower() \
            if 'category' in json_data['characteristics'] else None
        if body:
            with open('drive.txt', 'a+') as f:
                print(json_data['characteristics']['category']['title'], json_data['characteristics']['category']['id'], file=f)
        body = 'внедорожник/кроссовер' if body == 'внедорожник' \
            or body == 'кроссовер' else body
        body = 'хэтчбек' if body == 'хетчбэк' else body
        body = 'лифтбек' if body == 'лифтбэк' else body
        return BODY.get(body)

    def get_last_site_update():
        """Returns localized date"""
        if not json_data['date_created']:
            return TZ.localize(datetime.strptime(json_data['hot_date'][0:19], '%Y-%m-%dT%H:%M:%S'))
        return TZ.localize(datetime.strptime(json_data['date_created'][0:19], '%Y-%m-%dT%H:%M:%S'))

    def get_price():
        for price in json_data['price']:
            if price['currency'] == 'usd':
                return int(price['value'])

    def get_dtp():
        return bool(json_data['is_crashed'])

    def get_cleared():
        return bool(not json_data['is_not_cleared'])

    def get_link():
        return 'https://ab.ua' + json_data['permalink']

    def get_year():
        return json_data['year']

    def get_mileage():
        return json_data['mileage']

    def get_engine():
        return json_data['characteristics']['capacity'].get('number') if 'capacity' in json_data['characteristics'] else None

    def get_model():
        mark = json_data['make']['slug'].lower() if json_data['make']['slug'] else None
        model = json_data['model']['slug'].lower() if json_data['model']['slug'] else None
        if mark is not None and model is not None:
            return get_model_id(mark, model)

    def get_location():
        location = json_data['location'].get('title')
        return LOCATION.get(location.lower()) if location else None

    def get_fuel():
        fuel = json_data['characteristics']['engine']['title'][:6].lower() \
            if 'engine' in json_data['characteristics'] else None
        fuel = fuel + 'о' if fuel == 'электр' else fuel
        fuel = 'газ/бензин' if fuel == 'газ, б' else fuel
        return FUEL.get(fuel)

    def get_description():
        return json_data.get('description')

    def get_image():
        return json_data['photos'][0]['image'] if json_data['photos'] else None

    def get_sold():
        return bool(json_data['sold'] or not json_data['active'])

    def get_phone_url():
        return 'https://ab.ua/api/_posts/{}/phones/'.format(get_car_id())

    def get_seller():
        phones = [get_formatted_phone(phone) for phone in json.loads(requests.get(get_phone_url()).text)]
        seller = Seller.objects.filter(sellerphone__phone__in=phones).distinct().first()

        if not seller:
            seller = Seller.objects.create()

        seller.name = json_data['author']['first_name'] or json_data['agency']['title'] or json_data['contact_name']
        seller.dealer = bool(json_data['agency']['id'])
        seller.save()

        for phone in phones:
            SellerPhone.objects.update_or_create(seller=seller, phone=phone)
        return seller

    return {
        'model_id': get_model(),
        'seller': get_seller(),
        'sold': get_sold(),
        'gearbox': get_gearbox(),
        'location': get_location(),
        'fuel': get_fuel(),
        'year': get_year(),
        'mileage': get_mileage(),
        'engine': get_engine(),
        'description': get_description(),
        'body': get_body(),
        'image': get_image(),
        'dtp': get_dtp(),
        'drive': get_drive(),
        'cleared': get_cleared(),
        'last_site_update': get_last_site_update(),
        'price': get_price(),
        'ab_link': get_link(),
        'ab_car_id': get_car_id()
    }

class Ab:
    """Collects and updates car information from the site https://ab.ua/"""
    url = 'https://ab.ua/api/_posts/'

    @staticmethod
    def set_price(car, price):
        """Set price history"""
        price = int(price)
        price_history_obj = PriceHistory.objects.filter(car=car, site='AB').first()
        if car.price != price and ((price_history_obj and price_history_obj.price != price) or not price_history_obj):
            PriceHistory.objects.create(car=car, price=price, site='AB')

    def get_car_list_by_page(self, page):
        """Returns car list on page"""
        url = self.url + '?transport=1&page={0}'
        res = requests.get(url.format(page))
        car_list = []
        if res.status_code == 200:
            r_json = json.loads(res.text)
            car_list = r_json['results']
        else:
            print('{} page not found'.format(page))
        return car_list

    def parse(self, start, finish):
        """Creates Car model objects from inbound page list"""
        for page in range(start, finish):
            print('{} page of {}'.format(page, finish))
            for car_item in self.get_car_list_by_page(page):
                data = parse_data(car_item)
                if not data['sold']:
                    link = CarLink.objects.filter(link=data['ab_link']).first()
                    if not link and data['model_id']:
                        car = find_same_car(data, 'ab')
                        if car:
                            CarLink.objects.create(car=car, link=data['ab_link'], site='ab')
                            self.set_price(car, data['price'])
                        else:
                            car = Car.objects.create(**data)
                            CarLink.objects.create(car=car, link=data['ab_link'], site='ab')
                            for photo in car_item['photos']:
                                CarImage.objects.create(car=car, image=photo['image'])
                            PriceHistory.objects.create(car=car, price=data['price'], site='ab')

    def update(self, car):
        """Updates existing Car objects"""
        data = parse_data(self.url, car_id)
        if data['sold'] is True:
            car.sold = True
            car.save()
        else:
            if car.price != data['price']:
                self.set_price(car, data['price'])
                if car.price > data['price']:
                    car.price = data['price']
                    car.updated = now()
                    car.save()
