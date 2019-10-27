import json
import random
import string
import requests
from time import sleep

from bs4 import BeautifulSoup

from apps.main.models import *

from django.utils.timezone import get_current_timezone
from datetime import datetime
TZ = get_current_timezone()

from apps.parsers.choises import GEARBOX, FUEL, BODY, LOCATION
from apps.parsers.utils import get_model_id, find_same_car


# Оставляет в строке только цифры
class DigitsMixin:
    def __init__(self, keep=string.digits):
        self.comp = dict((ord(c),c) for c in keep)
    def __getitem__(self, k):
        return self.comp.get(k)

OD = DigitsMixin()


class Rst:
    url = 'http://rst.ua/oldcars/?task=newresults&make%5B%5D=0&year%5B%5D=0&year%5B%5D=0&price%5B%5D=0&price%5B%5D=0\
    &engine%5B%5D=0&engine%5B%5D=0&gear=0&fuel=0&drive=0&condition=0&from=sform&start={}'

    def __init__(self, pages):
        self.data_record(pages)

    @staticmethod
    def get_page(url):
        """Returns page content"""
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, 'lxml')
        return soup

    def get_ads_on_page(self, url):
        """Returns all ads on page"""
        soup = self.get_page(url)

        ad_url_list = []

        ads_1 = soup.find('div', class_='rst-page-wrap').find_all('div', class_='rst-ocb-i rst-ocb-i-premium rst-uix-radius')
        if ads_1:
            for item in ads_1:
                href = 'http://rst.ua' + item.find('a', class_='rst-ocb-i-a')['href']
                ad_url_list.append(href)

        ads_2 = soup.find('div', class_='rst-page-wrap').find_all('div', class_='rst-ocb-i rst-ocb-i-premium rst-uix-radius rst-ocb-i-crash')
        if ads_2:
            for item in ads_2:
                href = 'http://rst.ua' + item.find('a', class_='rst-ocb-i-a')['href']
                ad_url_list.append(href)

        ads_3 = soup.find('div', class_='rst-page-wrap').find_all('div', class_='rst-ocb-i rst-ocb-i-premium rst-uix-radius rst-ocb-i-blue')
        if ads_3:
            for item in ads_3:
                href = 'http://rst.ua' + item.find('a', class_='rst-ocb-i-a')['href']
                ad_url_list.append(href)

        return ad_url_list

    def get_ad_data(self, url):
        """Returns ad's data"""
        data = dict()
        soup = self.get_page(url)

        price_soup = soup.find('td', text='Цена') if soup.find('td', text='Цена') else soup.find('span', text='Цена')
        data['price'] = price_soup.find_next_sibling().find('span').find('span').text.translate(OD)

        year_mil_soup = soup.find('td', text='Год выпуска') if soup.find('td', text='Год выпуска') else soup.find('span', text='Год выпуска')
        data['year'] = year_mil_soup.find_next_sibling().find('a').text.translate(OD)
        data['mileage'] = int(year_mil_soup.find_next_sibling().find('span').text.translate(OD)) // 1000

        # engine, fuel
        engine_soup = soup.find('td', text='Двигатель') if soup.find('td', text='Двигатель') else soup.find('span', text='Двигатель')
        data['engine'] = engine_soup.find_next_sibling().find('strong').text[:3]
        fuel = engine_soup.find_next_sibling().find('span').text.replace('(','').replace(')','').lower()
        data['fuel'] = FUEL.get(fuel)

        # gearbox
        gearbox_soup = soup.find('td', text='КПП') if soup.find('td', text='КПП') else soup.find('span', text='КПП')
        gearbox = gearbox_soup.find_next_sibling().find('strong').text.lower()
        data['gearbox'] = GEARBOX.get(gearbox)

        # body
        body_soup = soup.find('td', text='Тип кузова') if soup.find('td', text='Тип кузова') else soup.find('span', text='Тип кузова')
        body = body_soup.find_next_sibling().find('strong').text.split()[0].lower()
        data['body'] = BODY.get(body)

        # location
        location_soup = soup.find('td', text='Область') if soup.find('td', text='Область') else soup.find('span', text='Область')
        location = location_soup.find_next_sibling().find('a').text.lower()
        data['location'] = LOCATION_ALL.get(location)

        date_soup = soup.find('td', text='Дата добавления') if soup.find('td', text='Дата добавления') else soup.find('span', text='Дата добавления')
        created = date_soup.find_next_sibling().find('span').text
        data['last_site_updatedAt'] = TZ.localize(datetime.strptime(created, '%d.%m.%Y'))

        mark_model = soup.find('div', class_='rst-uix-page-tree rst-uix-radius').find('a').find_next_sibling('a').find_next_sibling('a').find_next_sibling('a').text

        mark = mark_model.split()[0].lower()
        model = mark_model.split()[1].lower()

        data['model_id'] = get_model_id(mark, model)

        data['description'] = soup.find('div', class_='rst-page-oldcars-item-option-block-container rst-page-oldcars-item-option-block-container-desc rst-uix-block-more').text.strip() if \
            soup.find('div', class_='rst-page-oldcars-item-option-block-container rst-page-oldcars-item-option-block-container-desc rst-uix-block-more') else None

        images_soup = soup.find_all('a', class_='rst-uix-float-left rst-uix-radius')
        data['image'] = images_soup[0]['href'] if images_soup else None

        data['dtp'] = bool(soup.find('em', text="После ДТП"))
        data['rst_link'] = url
        return data

    def data_record(self, pages):
        """Parser"""
        for page in range(1, pages+1):
            print('get {} page'.format(page))
            sleep(random.randint(3, 5))
            for url in self.get_ads_on_page(self.url.format(page)):

                print('Start parsing {}'.format(url))
                sleep(random.randint(5, 10))

                data = self.get_ad_data(url)
                car = Car.objects.filter(
                    model_id=data['model_id'],
                    gearbox=data['gearbox'],
                    fuel=data['fuel'],
                    year=data['year'],
                    mileage=data['mileage'],
                    engine=data['engine'],
                    body=data['body'],
                    location=data['location'],
                    dtp=data['dtp'],
                    rst_link=''
                ).first()
                if car:
                    print(f' ###########################################')
                    print(f' #### Car {car.id} exists,add rst_link ####')
                    print(f' ###########################################')
                    car.rst_link = data['rst_link']
                    car.updatedAt = TZ.localize(datetime.now())
                    car.save()
                    if car.price != int(data['price']):
                        if PriceHistory.objects.filter(car=car, site='RST').first() and \
                            PriceHistory.objects.filter(car=car, site='RST').first().price != int(data['price']):
                            PriceHistory.objects.create(car=car, price=data['price'], site='RST')
                        else:
                            PriceHistory.objects.create(car=car, price=data['price'], site='RST')
        return print('Done')
