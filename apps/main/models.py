from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django.dispatch import receiver
from django.db.models.signals import post_save

from apps.main.car_choices import *
from apps.main.tasks import check_filters


class Mark(models.Model):
    name = models.CharField(max_length=128, blank=False)
    ria_id = models.IntegerField(null=True)
    eng = models.CharField(max_length=128, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Model(models.Model):
    name = models.CharField(max_length=128, blank=False)
    mark = models.ForeignKey(Mark, null=True, on_delete=models.CASCADE)
    ria_id = models.IntegerField(null=True)
    eng = models.CharField(max_length=128, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=128, blank=False)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Body(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Seller(models.Model):
    name = models.CharField(max_length=256, null=True)
    dealer = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)

    def __str__(self):
        return f'<SellerPhone: id={self.id} phone={self.sellerphone_set.first()}, dealer={self.dealer}, is_blocked={self.is_blocked}>'

    @property
    def car_count(self):
        """Returns the number of seller’s cars"""
        return sum([item.carlink_set.count() for item in self.car_set.all()])

    @property
    def status(self):
        """Returns seller status"""
        if self.car_count > 9:
            return 'Диллер' if self.dealer else 'Перекупщик'
        return 'Продавец'

    @property
    def is_dealer(self):
        if self.car_count >= 10:
            return True
        return False

    @property
    def get_phone(self):
        return self.phoneseller_set.first().phone

    def get_absolute_url(self):
        return reverse('seller', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        if self.is_dealer:
            self.dealer = True
        super().save(*args, **kwargs)


class SellerPhone(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    phone = models.CharField(max_length=12, unique=True)

    def __str__(self):
        return self.phone

class Car(models.Model):
    seller = models.ForeignKey(Seller, null=True, on_delete=models.SET_NULL)
    price = models.IntegerField(null=True)
    model = models.ForeignKey(Model, null=True, on_delete=models.SET_NULL)
    gearbox = models.IntegerField(choices=GEARBOX_CHOICE, null=True, blank=True)
    location = models.IntegerField(choices=LOCATION_CHOICE, null=True, blank=True)
    fuel = models.IntegerField(choices=FUEL_CHOICE, null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    mileage = models.IntegerField(null=True, blank=True)
    engine = models.FloatField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    body = models.IntegerField(choices=BODY_CHOICE, null=True, blank=True)
    image = models.CharField(max_length=256, null=True, blank=True)
    dtp = models.BooleanField(default=False)
    drive = models.IntegerField(choices=DRIVE_CHOICE, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(default=now)
    last_site_update = models.DateTimeField(blank=True, null=True)
    sold = models.BooleanField(default=False)
    cleared = models.BooleanField(default=True)
    olx_link = models.URLField(blank=True)
    ria_link = models.URLField(blank=True)
    ab_link = models.URLField(blank=True)
    bp_link = models.URLField(blank=True)
    ab_car_id = models.CharField(max_length=20, blank=True)
    rst_link = models.URLField(blank=True)

    class Meta:
        verbose_name_plural = 'Cars'
        ordering = ['-created']

    def __str__(self):
        return '{} {}'.format(self.model.mark if self.model else '', self.model)

    @property
    def price_history(self):
        if self.pricehistory_set.count() > 1:
            return True
        return False


# @receiver(post_save, sender=Car)
# def car_post_save_receiver(sender, instance, **kwargs):
#     if not instance.sold:
#         check_filters.delay(instance.pk)


class CarLink(models.Model):
    site = models.CharField(choices=SITE_CHOICE, max_length=3)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    link = models.URLField()

    def __str__(self):
        return self.link


class CarImage(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    image = models.URLField()

    def __str__(self):
        return self.image


class CarsComment(models.Model):
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE
    )
    comment = models.TextField()
    posted_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comment


class PriceHistory(models.Model):
    site = models.CharField(choices=SITE_CHOICE, max_length=3)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    price = models.IntegerField()
    date_set = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'price_history'

    def __str__(self):
        return f'<PriceHistory: price={self.price}, date_set={self.date_set}>'

    # def save(self, *args, **kwargs):
    #     if self.site == 'AR' or not bool(PriceHistory.objects.filter(car=self.car, site='AR').count()):
    #         self.car.price = self.price
    #         self.car.save()
    #     super().save(*args, **kwargs)


class FavouriteCar(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE
    )
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name_plural = 'Favourite Cars'

    def __str__(self):
        return f'<FavouriteCar: user={self.user}, car={self.car}'
