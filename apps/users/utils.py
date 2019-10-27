import re
import random
import requests
from django.core.cache import cache


def normalize_phone(phone):
    phone = re.sub(r'[+\s()-]', '', phone.strip())
    phone = '380' + phone[-9:]
    return phone


def normalize_email(email):
    return email.lower()


def valid_phone(phone):
    if not re.match(r'^[\d]{12}$', phone) or not phone.startswith('38'):
        return False
    return True


def single_message(phone, message):
    url = 'https://im.smsclub.mobi/sms/send'
    token = '4cbwZOguzteremJ'
    src_addr = '2Cars.Pro'
    headers = {'Authorization': 'Bearer {}'.format(token)}
    data = {
        'src_addr': src_addr,
        'phone': [phone],
        'message': message
    }
    res = requests.post(url, json=data, headers=headers)
    return res


def get_status(sms_id):
    url = 'https://im.smsclub.mobi/sms/status'
    token = '4cbwZOguzteremJ'
    headers = {'Authorization': 'Bearer {}'.format(token)}
    sms_ids = list()
    sms_ids.append(sms_id)
    data = {
        'id_sms': sms_ids,
    }
    res = requests.post(url=url, json=data, headers=headers)
    return res


def get_balance():
    url = 'https://im.smsclub.mobi/sms/balance'
    token = '4cbwZOguzteremJ'
    headers = {'Authorization': 'Bearer {}'.format(token)}
    res = requests.post(url=url, headers=headers)
    return res


def get_alfa():
    url = 'https://im.smsclub.mobi/sms/originator'
    token = '4cbwZOguzteremJ'
    headers = {'Authorization': 'Bearer {}'.format(token)}
    res = requests.post(url=url, headers=headers)
    return res


def _get_code(length=4):
    return random.sample(range(10**(length-1), 10**length), 1)[0]


def _verify_code(phone, code):
    return code == cache.get(phone)
