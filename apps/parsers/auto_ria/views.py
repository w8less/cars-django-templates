from django.http import JsonResponse
from django.views import View


class AutoRia(View):

    def get(self, req):
        print('done')
        return JsonResponse(dict(status='success'))
