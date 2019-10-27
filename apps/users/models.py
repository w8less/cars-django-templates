from django.urls import reverse
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.postgres.fields import JSONField
from urllib.parse import urlencode

from apps.users.managers import CustomUserManager
from apps.users.utils import single_message


class Profile(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=128, blank=True)
    email = models.EmailField(max_length=128, unique=True, db_index=True)
    phone = models.CharField(max_length=12, unique=True, db_index=True)
    descriptions = models.TextField(blank=True)
    expired = models.DateTimeField(default=timezone.now() + timezone.timedelta(days=3))
    PROFILE_TYPE = (
        (0, 'АвтоБизнесмен'),
        (1, 'Автомобильная компания'),
        (2, 'Частное лицо'),
    )
    profile_type = models.IntegerField(choices=PROFILE_TYPE, default=0)
    PLAN_TYPE = (
        (0, 'Бесплатный'),
        (1, 'Премиум'),
        (2, 'Pro'),
    )
    plan_type = models.IntegerField(choices=PLAN_TYPE, default=1)
    telegram_id = models.IntegerField(default=0)
    comment = models.TextField(blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone']

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    @property
    def get_full_name(self):
        return self.name

    @property
    def get_short_name(self):
        return self.name

    @property
    def get_phone_normal(self):
        normal_phone = '+38 ({}) {}-{}-{}'.format(self.phone[2:5], self.phone[5:8], self.phone[8:10], self.phone[10:])
        return normal_phone

    def send_message(self, text):
        single_message(self.phone, text)

    @property
    def get_absolute_url(self):
        return reverse('auth:profile-detail', kwargs={'pk': self.pk})

    @property
    def is_paid(self):
        return bool(self.expired > timezone.now() and self.plan_type != 0)

    @property
    def spent_money(self):
        order_qs = self.order_set.filter(confirmed=True)
        return sum([order.plan.price for order in order_qs])

    def check_paid(self):
        if self.expired < timezone.now() and self.plan_type != 0:
            self.plan_type = 0


class NewFilter(models.Model):
    name = models.CharField(max_length=256, blank=True)
    description = models.TextField(blank=True)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    data = JSONField(default=dict)
    is_active = models.BooleanField(default=True)

    def get_models(self):
        return self.data.get('model')

    def get_marks(self):
        return self.data.get('model__mark')

    def get_data(self):
        return {key: value for key, value in self.data.items() if value and not isinstance(value, list)}

    def get_absolute_url(self):
        query = '?' + urlencode(self.get_data)
        for model in self.get_models():
            query += f'&model={model}'
        for mark in self.get_marks():
            query += f'&model__mark={mark}'
        return reverse('all-car') + query

    def get_filter(self):
        query = models.Q()
        for item in list(map(lambda x, y: {'model__mark': x, 'model': y} if y else {'model__mark': x}, self.get_marks(), self.get_models())):
            query |= models.Q(**item)
        return query, self.get_data()

    def __str__(self):
        return self.user.name


class UserFilter(models.Model):
    name = models.CharField(max_length=256, blank=True)
    description = models.TextField(blank=True)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    model = models.IntegerField(null=True, blank=True)
    mark = models.IntegerField(null=True, blank=True)
    gearbox = models.IntegerField(null=True, blank=True)
    location = models.IntegerField(null=True, blank=True)
    year_start = models.IntegerField(null=True, blank=True)
    year_end = models.IntegerField(null=True, blank=True)
    price_start = models.IntegerField(null=True, blank=True)
    price_end = models.IntegerField(null=True, blank=True)
    CLEARED_CHOICE = (
        (None, 'Любая регистрация'),
        (0, 'Не растаможенные'),
        (1, 'Растаможенные'),
    )
    cleared = models.IntegerField(choices=CLEARED_CHOICE, default=None, null=True, blank=True)
    DTP_CHOICE = (
        (None, 'Все'),
        (0, 'Без ДТП'),
        (1, 'После ДТП')
    )
    dtp = models.IntegerField(choices=DTP_CHOICE, default=None, null=True, blank=True)
    blocked = models.BooleanField(default=False)
    dealer = models.BooleanField(default=False)
    fuel = models.IntegerField(null=True, blank=True)
    mileage_start = models.IntegerField(null=True, blank=True)
    mileage_end = models.IntegerField(null=True, blank=True)
    engine = models.IntegerField(null=True, blank=True)
    body = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    filtered_fields = (
        ('mark', 'model__mark'),
        ('model', 'model'),
        ('gearbox', 'gearbox'),
        ('location', 'location'),
        ('engine', 'engine'),
        ('body', 'body'),
        ('fuel', 'fuel'),
        ('cleared', 'cleared'),
        ('dtp', 'dtp'),
        ('blocked', 'seller__is_blocked'),
        ('dealer', 'seller__dealer'),
        ('year_start', 'year__gte'),
        ('year_end', 'year__lte'),
        ('price_start', 'price__gte'),
        ('price_end', 'price__lte'),
        ('mileage_start', 'mileage__gte'),
        ('mileage_end', 'mileage__lte'),
    )

    class Meta:
        verbose_name_plural = 'User filters'

    def __str__(self):
        return f'User filter #{self.pk}'

    def is_normal(self, field):
        return getattr(self, field) is not False and getattr(self, field) is not None

    def get_url(self):
        url = '/all-car/?'
        for old, new in self.filtered_fields:
            if self.is_normal(old):
                url += f'&{new}={getattr(self, old)}'
        return url.replace('True', 'on')

    def get_filtered_fields(self):
        return {new_field: getattr(self, old_field) for old_field, new_field in self.filtered_fields if self.is_normal(old_field)}


class InfoMessage(models.Model):
    message = models.TextField(blank=True, default='')
