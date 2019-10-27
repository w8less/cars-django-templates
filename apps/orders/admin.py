from django.contrib import admin

from apps.orders.models import Order, Plan


@admin.register(Order)
class Order(admin.ModelAdmin):
    list_display = ['user', 'plan', 'confirmed']


@admin.register(Plan)
class Plan(admin.ModelAdmin):
    list_display = ['name', 'days', 'price']
