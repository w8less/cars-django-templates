from django.conf import settings
from django.urls import reverse
from django.views.generic import ListView, View, RedirectView

from django.utils import timezone
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test, login_required
from django.views.decorators.csrf import csrf_exempt

from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from apps.orders.models import Order
from apps.orders.liqpay import LiqPay

class OrderListView(ListView):
    # model = Order
    queryset = Order.objects.order_by('-id')
    template_name = 'order_list.html'
    context_object_name = 'order_list'

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class OrderSetView(View):

    @method_decorator(login_required)
    def post(self, request):
        plan = request.POST.get('plan')
        user = request.user
        host = request.get_host()
        if plan:
            public_key = settings.LIQPAY_PUBLIC_KEY
            private_key = settings.LIQPAY_PRIVATE_KEY
            order = Order.objects.create(user=user, plan_id=plan)
            liqpay = LiqPay(public_key, private_key)
            params = {
                'action': 'pay',
                'amount': order.plan.price,
                'currency': 'UAH',
                'description': 'Подписка {} jet.2cars.pro'.format(order.plan.name),
                'order_id': f'{order.id}{user.phone}',
                'version': '3',
                'result_url': 'https://{}/order/redirect/'.format(host),
                'server_url': 'https://{}/order/confirm/'.format(host)
            }
            payment_url = liqpay.cnb_form(params)
            return JsonResponse({'button': payment_url})
        else:
            return HttpResponseRedirect(reverse('auth:profile'))


class OrderConfirmedView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        public_key = settings.LIQPAY_PUBLIC_KEY
        private_key = settings.LIQPAY_PRIVATE_KEY
        liqpay = LiqPay(public_key, private_key)
        data = request.POST.get('data')
        signature = request.POST.get('signature')
        sign = liqpay.str_to_sign(public_key + data + private_key)

        if sign == signature:
            print('good')
        data = liqpay.decode_data_from_str(data)
        if data['status'] == 'success':
            order = Order.objects.get(id=data['order_id'][:-12])
            order.confirm()
        return JsonResponse({'message':'ok'})

    def get(self, request):
        req = {'signature': '7ZoCmV5sEygJOq6oa7lYEXSeZNM=', 'data': 'eyJhY3Rpb24iOiJwYXkiLCJwYXltZW50X2lkIjoxMTMxNjU2MTU0LCJzdGF0dXMiOiJzdWNjZXNzIiwidmVyc2lvbiI6MywidHlwZSI6ImJ1eSIsInBheXR5cGUiOiJjYXJkIiwicHVibGljX2tleSI6Imk3NzExODQ5MzA4MSIsImFjcV9pZCI6NDE0OTYzLCJvcmRlcl9pZCI6IjEzODA5OTM2NTY1NzgiLCJsaXFwYXlfb3JkZXJfaWQiOiJXTkIxV0lVUzE1Njk4MDU2ODQxMTM1NTUiLCJkZXNjcmlwdGlvbiI6ItCf0L7QtNC/0LjRgdC60LAg0J/RgNC+0LHQvdGL0LkgamV0LjJjYXJzLnBybyIsInNlbmRlcl9waG9uZSI6IjM4MDk5MzY1NjU3OCIsInNlbmRlcl9jYXJkX21hc2syIjoiNTE2Nzk4Kjc1Iiwic2VuZGVyX2NhcmRfYmFuayI6InBiIiwic2VuZGVyX2NhcmRfdHlwZSI6Im1jIiwic2VuZGVyX2NhcmRfY291bnRyeSI6ODA0LCJpcCI6IjIxMy4xMTEuODQuMjEzIiwiYW1vdW50IjoxLjAsImN1cnJlbmN5IjoiVUFIIiwic2VuZGVyX2NvbW1pc3Npb24iOjAuMCwicmVjZWl2ZXJfY29tbWlzc2lvbiI6MC4wMywiYWdlbnRfY29tbWlzc2lvbiI6MC4wLCJhbW91bnRfZGViaXQiOjEuMCwiYW1vdW50X2NyZWRpdCI6MS4wLCJjb21taXNzaW9uX2RlYml0IjowLjAsImNvbW1pc3Npb25fY3JlZGl0IjowLjAzLCJjdXJyZW5jeV9kZWJpdCI6IlVBSCIsImN1cnJlbmN5X2NyZWRpdCI6IlVBSCIsInNlbmRlcl9ib251cyI6MC4wLCJhbW91bnRfYm9udXMiOjAuMCwiYXV0aGNvZGVfZGViaXQiOiI2MTExNDciLCJycm5fZGViaXQiOiIwMDEzNjYzOTA4OTgiLCJtcGlfZWNpIjoiNyIsImlzXzNkcyI6ZmFsc2UsImxhbmd1YWdlIjoicnUiLCJjcmVhdGVfZGF0ZSI6MTU2OTgwNTY2NzUzMSwiZW5kX2RhdGUiOjE1Njk4MDU2ODY1NTIsInRyYW5zYWN0aW9uX2lkIjoxMTMxNjU2MTU0fQ=='}
        data = req.get('data')
        public_key = settings.LIQPAY_PUBLIC_KEY
        private_key = settings.LIQPAY_PRIVATE_KEY
        liqpay = LiqPay(public_key, private_key)
        data = liqpay.decode_data_from_str(data)
        if data['status'] == 'success':
            order = Order.objects.get(id=data['order_id'][:-12])
            order.confirm()
        return JsonResponse({'test':'ok'})


class OrderConfirmRedirectView(RedirectView):
    permanent = True
    pattern_name = 'auth:profile'

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


# liqpay data callback
# {
#     'action': 'pay',
#     'payment_id': 1127547089,
#     'status': 'success',
#     'version': 3,
#     'type': 'buy',
#     'paytype': 'card',
#     'public_key': 'i77118493081',
#     'acq_id': 414963,
#     'order_id': '7380993656578',
#     'liqpay_order_id': 'TLVJZUJG1569322649119789',
#     'description': 'Подписка Пробный jet.2cars.pro',
#     'sender_phone': '380731853494',
#     'sender_card_mask2': '516798*75',
#     'sender_card_bank': 'pb',
#     'sender_card_type': 'mc',
#     'sender_card_country': 804,
#     'ip': '176.100.5.206',
#     'amount': 1.0,
#     'currency': 'UAH',
#     'sender_commission': 0.0,
#     'receiver_commission': 0.03,
#     'agent_commission': 0.0,
#     'amount_debit': 1.0,
#     'amount_credit': 1.0,
#     'commission_debit': 0.0,
#     'commission_credit': 0.03,
#     'currency_debit': 'UAH',
#     'currency_credit': 'UAH',
#     'sender_bonus': 0.0,
#     'amount_bonus': 0.0,
#     'authcode_debit': '333127',
#     'rrn_debit': '001360611213',
#     'mpi_eci': '7',
#     'is_3ds': False,
#     'language': 'ru',
#     'create_date': 1569322594291,
#     'end_date': 1569322650787,
#     'transaction_id': 1127547089
# }