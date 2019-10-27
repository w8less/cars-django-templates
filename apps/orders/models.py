from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone


class Plan(models.Model):
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=128)
    days = models.IntegerField()
    price = models.IntegerField()
    PLAN_TYPE = (
        (1, 'Премиум'),
        (2, 'Pro'),
    )
    plan_type = models.IntegerField(choices=PLAN_TYPE, default=0)

    def __str__(self):
        return f'Plan id={self.id}, plan={self.name}, price={self.price}'


class Order(models.Model):
    user = models.ForeignKey(get_user_model(), null=True, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True, default='LiqPay')
    confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f'Order id={self.id}, plan={self.plan.name}, user={self.user.name}'

    def confirm(self):
        if not self.confirmed:
            self.confirmed = True
            self.save()

    def save(self, *args, **kwargs):
        if self.confirmed is True:
            if self.user.plan_type == self.plan.plan_type:
                self.user.expired += timezone.timedelta(days=self.plan.days)
            else:
                self.user.plan_type = self.plan.plan_type
                self.user.expired = timezone.now() + timezone.timedelta(days=self.plan.days)
            self.user.save()
        super().save(*args, **kwargs)
