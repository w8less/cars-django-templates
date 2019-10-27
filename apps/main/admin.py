from django.contrib import admin
from django.utils.html import format_html

from apps.main.models import Mark, Model, Car, CarImage, CarLink, PriceHistory, Seller, CarsComment, FavouriteCar, SellerPhone

admin.site.register(Mark)
admin.site.register(Model)

class CarInline(admin.TabularInline):
    model = Car
    extra = 0
    fields = ['show_url']
    readonly_fields = ['show_url']

    def show_url(self, obj):
        return format_html("<a href='/admin/main/car/{pk}' target='_blank'>{obj}</a>", pk=obj.pk, obj=obj)
    show_url.short_description = "car"

    def show_ab_link(self, obj):
        return format_html("<a href='{url}' target='_blank'>{url}</a>", url=obj.ab_link)
    show_ab_link.short_description = "ab link"


class SellerPhoneInline(admin.TabularInline):
    model = SellerPhone
    extra = 0


class CarImageInline(admin.TabularInline):
    model = CarImage
    extra = 0


class CarLinkInline(admin.TabularInline):
    model = CarLink
    extra = 0


class CarsCommentInline(admin.TabularInline):
    model = CarsComment
    extra = 0


class PriceHistoryInline(admin.TabularInline):
    model = PriceHistory
    extra = 0


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['model', 'sold', 'gearbox', 'show_ria_link', 'show_ab_link', 'show_olx_link', 'created', 'updated', 'last_site_update']
    readonly_fields = ['model', 'seller']
    inlines = [PriceHistoryInline, CarsCommentInline, CarLinkInline, CarImageInline]

    def show_ria_link(self, obj):
        return format_html("<a href='{url}' target='_blank'>{url}</a>", url=obj.ria_link)
    show_ria_link.short_description = "ria link"

    def show_ab_link(self, obj):
        return format_html("<a href='{url}' target='_blank'>{url}</a>", url=obj.ab_link)
    show_ab_link.short_description = "ab link"

    def show_olx_link(self, obj):
        return format_html("<a href='{url}' target='_blank'>{url}</a>", url=obj.olx_link)
    show_olx_link.short_description = "olx link"


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ['name', 'dealer']
    inlines = [SellerPhoneInline, CarInline]


@admin.register(FavouriteCar)
class FavouriteCar(admin.ModelAdmin):
    list_display = ['user', 'car']
