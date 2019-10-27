from django.urls import path
from apps.analitic.views import AnaliticView, AnaliticMileageView, AnaliticSelltimeView

app_name = 'analitic'

urlpatterns = [
    path('', AnaliticView.as_view(), name='index'),
    path('mileage/', AnaliticMileageView.as_view(), name='mileage'),
    path('selltime/', AnaliticSelltimeView.as_view(), name='selltime'),
]
