from django.urls import path

from apps.telegram.views import SendMessageView, TelegramSetHook, TelegramHook


app_name = 'telegram'

urlpatterns = [
    path('', TelegramHook.as_view(), name='hook'),
    path('set_hook/', TelegramSetHook.as_view(), name='set-hook'),
    path('send_message/', SendMessageView.as_view(), name='send-message'),
]
