from django.views.generic import View
from django.http import HttpResponse

from .parser import Rst

class RstView(View):

    def get(self, request):
        Rst(10)

        return HttpResponse('DONE')
