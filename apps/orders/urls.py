from django.urls import path

from apps.orders.views import (
    OrderListView,
    OrderSetView,
    OrderConfirmedView,
    OrderConfirmRedirectView,
)

app_name = 'order'

urlpatterns = [
    path('', OrderListView.as_view(), name='list'),
    path('set/', OrderSetView.as_view(), name='set'),
    path('confirm/', OrderConfirmedView.as_view(), name='confirm'),
    path('redirect/', OrderConfirmRedirectView.as_view(), name='redirect'),
]
