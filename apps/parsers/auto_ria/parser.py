import re
import datetime
import json
import threading
from django.utils import timezone
from django.utils.timezone import get_current_timezone
import requests

from apps.main.models import Car, CarImage, Seller, SellerPhone, PriceHistory
from apps.parsers.choises import LOCATION, FUEL, GEARBOX
from apps.parsers.utils import get_model_id, find_same_car

TZ = get_current_timezone()


class WordsFormater:

    def engine_parse(self, word: str):
        if word == 'Не указано':
            return None
        elif word.find(', ') == -1:
            return None
        return float(word[word.find(', ') + 1:word.find('л.')])

    def fuel_parse(self, word: str):
        return word[:word.find(',')].lower()

    def formating(self, word: str):
        return word.lower().replace(' ', '')

    # def format_phone(self, word: str):
    #     integers = '0123456789'
    #     response = word
    #     for liter in word:
    #         if liter not in integers:
    #             response = response.replace(liter, '')
    #     if response[:3] != '380':
    #         response = f'38{response}'
    #     return response

    def format_phone(self, phone):
        """Returns formatted phone number"""
        phone = re.sub(r'\D', '', phone)
        if len(phone) != 12:
            phone = '380' + phone[-9:]
        return phone

    def check_dtp(self, word: str):
        exept = 'После ДТП'
        if exept in word:
            return True
        return False

    def format_date(self, word: str):
        if len(word) <= 10:
            return None
        return TZ.localize(datetime.datetime.strptime(word, '%Y-%m-%d %H:%M:%S'))


class AutoRiaInnerParse(WordsFormater):
    list_posts_way = 'http://auto.ria.com/blocks_search_ajax/search/?countpage={}&category_id=1&page={}&saledParam=2'
    post_way = 'https://auto.ria.com/demo/bu/searchPage/v2/view/auto/{}/?lang_id=2'

    def __init__(self):
        self.first_data = json.loads(requests.get(self.list_posts_way.format(10, 0)).content)
        t1 = threading.Thread(target=self.runner, args=(0, 500))
        # t2 = threading.Thread(target=self.runner, args=(501, 1000))
        # t3 = threading.Thread(target=self.runner, args=(1001, 1500))
        # t4 = threading.Thread(target=self.runner,
        #                       args=(1501, self.first_data['result']['search_result']['count'] // 100))
        t1.start()
        # t2.start()
        # t3.start()
        # t4.start()
        t1.join()
        # t2.join()
        # t3.join()
        # t4.join()

    def set_seller(self, phone):
        phone = self.format_phone(phone)
        seller = Seller.objects.filter(sellerphone__phone=phone).first()
        if not seller:
            seller = Seller.objects.create()
            SellerPhone.objects.update_or_create(seller=seller, phone=phone)
        return seller

    def find_model(self, data: dict):
        return get_model_id(data['markNameEng'], data['modelNameEng'])

    def set_price(self, price_int: int, car):
        price = PriceHistory(price=price_int, date_set=timezone.now(), car=car, site='ria')
        price.save()

    def set_car(self, data: dict) -> dict:
        car = dict(model_id=self.find_model(data),
                   gearbox=GEARBOX.get(self.formating(data['autoData']['gearboxName'])),
                   location=LOCATION.get(self.formating(data['stateData']['regionName'])),
                   fuel=FUEL.get(self.fuel_parse(data['autoData']['fuelName'])),
                   engine=self.engine_parse(data['autoData']['fuelName']),
                   description=data['autoData']['description'],
                   year=data['autoData']['year'],
                   mileage=data['autoData']['raceInt'],
                   seller=self.set_seller(data['userPhoneData']['phone']),
                   body=(data['autoData'].get('bodyId')),
                   image=data['photoData']['seoLinkF'],
                   dtp=self.check_dtp(data['infoBarText']),
                   sold=data['autoData']['isSold'],
                   cleared=not bool(data['autoData']['custom']),
                   ria_link='https://auto.ria.com' + data['linkToView'],
                   created=self.format_date(data['addDate']),
                   updated=timezone.now(),
                   last_site_update=self.format_date(data['updateDate']),
                   price=data['USD']
                   )
        return car

    def ar_same_car(self, car_dict: dict, price: int):
        car_obj = find_same_car(car_dict, 'ar')
        if car_obj:
            car_obj.ria_link = car_dict['ria_link']
            car_obj.updated = car_dict['updated']
            car_obj.save()
            self.set_price(price, car_obj)
        return car_obj

    def runner(self, start, finish):
        for i in range(start, finish):
            start_data = json.loads(requests.get(self.list_posts_way.format(100, i)).content)
            for ids in start_data['result']['search_result']['ids']:
                try:
                    data = json.loads(requests.get(self.post_way.format(ids)).content)
                except: pass
                car_dict = self.set_car(data)
                if car_dict['model_id']:
                    same_car = self.ar_same_car(car_dict, data['USD'])
                    if not same_car:
                        print('car save()')
                        car_obj = Car(**car_dict)
                        car_obj.save()
                        CarImage.objects.create(car=car_obj, image=data['photoData']['seoLinkF'])
                        self.set_price(data['USD'], car_obj)
                else:
                    print('car not save Mark:{}, model:{}, link: https://auto.ria.com{}'.format(
                        data["markNameEng"], data[
                            "modelNameEng"], data["linkToView"]))


class AutoRiaUpdateParse(AutoRiaInnerParse):
    list_posts_way = 'http://auto.ria.com/blocks_search_ajax/search/?countpage={}&category_id=1&page={}'
    post_way = 'https://auto.ria.com/demo/bu/searchPage/v2/view/auto/{}/?lang_id=2'

    def __init__(self, hours_updater: int):
        # count = 0
        self.hours_updater = hours_updater
        first_data = json.loads(requests.get(self.list_posts_way.format(100, 0)).content)
        t1 = threading.Thread(target=self.runner, args=(0, 500))
        t2 = threading.Thread(target=self.runner, args=(501, 1000))
        t3 = threading.Thread(target=self.runner, args=(1001, 1500))
        t4 = threading.Thread(target=self.runner, args=(1501, first_data['result']['search_result']['count'] // 100))
        t1.start()
        t2.start()
        t3.start()
        t4.start()
        t1.join()
        t2.join()
        t3.join()
        t4.join()

    def time_stack(self, updated: str):
        updated = TZ.localize(datetime.datetime.strptime(updated, '%Y-%m-%d %H:%M:%S'))
        start = timezone.now() - timezone.timedelta(hours=self.hours_updater)
        updated = updated.timestamp()
        if start.timestamp() < updated < timezone.now().timestamp():
            return True
        return False

    def runner(self, start, finish):
        for i in range(start, finish):
            start_data = json.loads(requests.get(self.list_posts_way.format(100, i)).content)
            for ids in start_data['result']['search_result']['ids']:
                data = json.loads(requests.get(self.post_way.format(ids)).content)
                if self.time_stack(data['updateDate']):
                    car = Car.objects.filter(ria_link='https://auto.ria.com' + data['linkToView']).first()
                    if data['autoData']['isSold']:
                        if car:
                            car.sold = True
                            car.save()
                        print(f'sold car {data["linkToView"]}')
                    else:
                        model = self.find_model(data)
                        if model:
                            if car and data["USD"] != car.price:
                                print(f'updates price {data["USD"]}, mark {data["markName"]}')
                                self.set_price(price_int=data['USD'], car=car)
                            elif car is None:
                                car_dict = self.set_car(data)
                                same_car = self.ar_same_car(car_dict, data['USD'])
                                if not same_car:
                                    print('create car')
                                    car_obj = Car(**car_dict)
                                    car_obj.save()
                                    self.set_price(data['USD'], car_obj)
                        else:
                            print('lol')
                else:
                    print('lol2')


# {'EUR': 11247,
#  'UAH': 336296,
#  'USD': 12700,
#  'addDate': '2019-06-09 17:17:04',
#  'auctionPossible': True,
#  'autoData': {'active': False,
#               'autoId': 24490777,
#               'bodyId': 2,
#               'categoryId': 1,
#               'categoryNameEng': 'legkovie',
#               'custom': 0,
#               'description': 'Кому нужен идеальный автомобиль, звоните! '
#                              'Renault MEGANE 1.6 MEGANE *BOSE*2014 FACELIFT '
#                              'СВЕЖЕзагнан в Украину. Авто в отличном '
#                              'состоянии. 100% НЕ КРАШЕНА НИ ОДНА ДЕТАЛЬ. '
#                              'РЕАЛЬНЫЙ ПРОБЕГ!!!! ИНДИВИДУАЛЬНАЯ комплектация: '
#                              'Подогрев сидений, Раздельный климат контроль, '
#                              'Круиз контроль,Полный электропакет, Подогрев '
#                              'зеркал и стекол, Задние парктроники, Функция '
#                              'свободные руки, Линзы, Передние и задние '
#                              'противотуманные фонари, Салон с кожаными '
#                              'вставками, Аудио система ВОSE, Электроручник, '
#                              'Старт-стопная система, Отчет расхода топлива, '
#                              'Очень экономная- средний расход 4,6л., 6-ти '
#                              'ступка 96квт. 131л.с. V- 1,6., Подключение тел. '
#                              'по блютуз, Громкая связь, Вазможность слушать '
#                              'музику из интернета, Отличная акустика - 6 '
#                              'динамиков, Русскоязычная навигация, AUX-вход, '
#                              'слот для карт памяти, резина летняя 100% '
#                              'мишелин, Диски на 17", заводская тонировка.',
#               'fromArchive': False,
#               'fuelName': 'Дизель, 1.6 л.',
#               'fuelNameEng': 'dizel',
#               'gearboxName': 'Ручная / Механика',
#               'isSold': True,
#               'mainCurrency': 'USD',
#               'onModeration': False,
#               'race': '140 тыс. км',
#               'raceInt': 140,
#               'statusId': 1,
#               'subCategoryNameEng': 'universal',
#               'version': ' *Bose*',
#               'withVideo': True,
#               'year': 2015},
#  'badges': [],
#  'canSetSpecificPhoneToAdvert': False,
#  'checkedVin': {'checkDate': '12.06.2019',
#                 'hasRestrictions': False,
#                 'isChecked': False,
#                 'isShow': False,
#                 'linkToReport': '/vin-check/auto/24490777/',
#                 'vin': 'VF1KZNA0х50хххх65'},
#  'chipsCount': 0,
#  'cityLocative': 'Борисполе',
#  'dealer': {'id': 0,
#             'link': '',
#             'logo': '',
#             'name': '',
#             'packageId': 0,
#             'type': '',
#             'typeId': 0},
#  'dontComment': 1,
#  'exchangePossible': False,
#  'exchangeType': 'Любой',
#  'exchangeTypeId': 0,
#  'expireDate': '2019-07-09 17:17:04',
#  'hasWebP': 2,
#  'infoBarText': '',
#  'isAutoAddedByPartner': False,
#  'isLeasing': 0,
#  'levelData': {'expireDate': '2019-06-12 17:22:08',
#                'hotType': '',
#                'label': 0,
#                'level': 103},
#  'linkToView': '/auto_renault_megane_24490777.html',
#  'locationCityName': 'Борисполь',
#  'markId': 62,
#  'markName': 'Renault',
#  'markNameEng': 'renault',
#  'modelId': 586,
#  'modelName': 'Megane',
#  'modelNameEng': 'megane',
#  'moderatedAbroad': False,
#  'oldTop': {'expireDate': '', 'isActive': False},
#  'optionStyles': [],
#  'partnerId': 0,
#  'photoData': {'count': 97,
#                'seoLinkB': 'https://cdn1.riastatic.com/photosnew/auto/photo/renault_megane__281200166b.jpg',
#                'seoLinkF': 'https://cdn1.riastatic.com/photosnew/auto/photo/renault_megane__281200166f.jpg',
#                'seoLinkM': 'https://cdn1.riastatic.com/photosnew/auto/photo/renault_megane__281200166m.jpg',
#                'seoLinkSX': 'https://cdn1.riastatic.com/photosnew/auto/photo/renault_megane__281200166sx.jpg'},
#  'realtyExchange': False,
#  'secureKey': 'b1ebf1930f92671427e4eddaea251dbd',
#  'sendComments': 0,
#  'soldDate': '2019-06-11 15:36:49',
#  'stateData': {'cityId': 212,
#                'linkToCatalog': '/city/borispol/',
#                'name': 'Киев',
#                'regionName': 'Киевская',
#                'regionNameEng': 'kiev',
#                'stateId': 10,
#                'title': 'Поиск объявлений по городу Борисполь'},
#  'title': 'Renault Megane  *Bose*',
#  'updateDate': '2019-06-09 8:23:30',
#  'userBlocked': [],
#  'userHideADSStatus': False,
#  'userId': 1301047,
#  'userPhoneData': {'phone': '(099) 382 10 51', 'phoneId': '1053017'},
#  'withInfoBar': False}
