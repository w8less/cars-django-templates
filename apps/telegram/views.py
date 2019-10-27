import json
from django.urls import reverse
from django.views.generic import View
from django.http import JsonResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import get_user_model
from apps.telegram.tasks import send_message
from apps.telegram.config import BOT


class SendMessageView(View):

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        chat_id = request.POST.get('chat_id')
        text = request.POST.get('message')
        profile_pk = request.POST.get('pk')
        if chat_id and text:
            send_message.delay(chat_id, text=text)
            return HttpResponseRedirect(reverse('auth:profile-detail', kwargs={'pk':profile_pk}))
        elif not chat_id and text:
            for user in get_user_model().objects.exclude(telegram_id=0):
                send_message.delay(user.telegram_id, text=text)
            return HttpResponseRedirect(reverse('auth:profile-list'))
        return JsonResponse({'message':'bad'}, status=400)


class TelegramSetHook(View):

    def get(self, request):
        url = 'https://{}/{}'.format(request.get_host(), 'telegram/')
        print(url)
        BOT.set_webhook(url)
        return JsonResponse({'message':'ok'}, status=200)


class TelegramHook(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        r = json.loads(request.body)
        telegram_id = r['message']['from']['id']
        message_id = r['message']['message_id']
        message = r['message']['text']
        if '/start' in message and len(message) > 7:
            profile_id = message.split()[1] if len(message.split()) > 1 and message.split()[1].isdigit() else 0
            profile = get_user_model().objects.filter(id=profile_id).first()
            if profile and not profile.telegram_id:
                profile.telegram_id = telegram_id
                profile.save()
                text = '''*Спасибо за то что ты с нами!*

Мы хотим быть тебе максимально полезны!
Поэтому постоянно улучшаем и дорабатываем наш сервис [jet2cars.site](https://jet2cars.site/)

Если хочешь купить себе машину,
Или, возможно, ты занимаешься покупкой авто на постоянной основе...
В любом случае тебе хочется купить хороший автомобиль,
в своем регионе, за адекватные деньги!

[JET](https://jet2cars.site/) тебе будет в этом очень полезен!

*Настраивай и сохраняй фильтры и ты будешь первым получать информацию о новых автомобилях!!!*'''
                BOT.send_message(telegram_id, text, parse_mode='Markdown')
            else:
                BOT.delete_message(telegram_id, message_id)
        else:
            BOT.delete_message(telegram_id, message_id)
        return JsonResponse({'ok': True})
