from django.urls import path

from apps.users.views import (
    LoginView,
    LogoutView,
    RegistrationView,
    ProfileView,
    SendCodeView,
    TelegramConnectView,
    ProfileListView,
    ProfileDetailView,
    ProfileUpdateView,
    ProfileDeleteView,

    UserFilterUpdateView,
    UserFilterChangeView,

    InfoMessageView,
)

app_name = 'auth'

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('login/', LoginView.as_view(), name='login'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('send_code/', SendCodeView.as_view(), name='send-code'),
    path('telegram/connect/', TelegramConnectView.as_view(), name='telegram-connect'),
    path('profiles/', ProfileListView.as_view(), name='profile-list'),
    path('profiles/<int:pk>/', ProfileDetailView.as_view(), name='profile-detail'),
    path('profiles/<int:pk>/update/', ProfileUpdateView.as_view(), name='profile-update'),
    path('profiles/<int:pk>/delete/', ProfileDeleteView.as_view(), name='profile-delete'),
    path('profiles/filters/', UserFilterChangeView.as_view(), name='user-filter-change'),
    path('profiles/filters/<int:pk>/', UserFilterUpdateView.as_view(), name='user-filter-update'),

    path('info-message/', InfoMessageView.as_view(), name='info-message'),

]
