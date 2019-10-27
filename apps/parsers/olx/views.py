import requests
from django.http import JsonResponse
from django.views.generic.base import View
from lxml import html
from time import sleep
from threading import Thread

from apps.parsers.besplatka.utils import bp_slicer_of_pages
from apps.parsers.olx.parser import OLXInner, update_olx_util


class OLXView(View):

    def get(self, request):
        for ind, i in enumerate(bp_slicer_of_pages(1, 200)):
            OLXInner()
            # update_olx_util()
            print('done !!')
        return JsonResponse(dict(status='success'))


def run(request):
    url = 'https://www.olx.ua/transport/legkovye-avtomobili/'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36 OPR/60.0.3255.109'
    url_paging = '?page={}'
    page_numbers = range(2, 500)
    list_pages = [url + url_paging.format(i) for i in page_numbers]
    list_pages.append(url)

    def process(urls):
        for url_ in urls:
            page = requests.get(url_, headers={'User-Agent': user_agent})
            web_page = html.fromstring(page.content)
            posts_list = web_page.xpath('//a[contains(@class, "marginright5 link linkWithHash detailsLink")]/@href')
            # sleep(1)
            for idx, post_url in enumerate(posts_list):
                print(f'link #{idx}, {post_url}')
                sleep(15)
                print('sleep 15')
                # olx = OLX(post_url)
                # olx.start()
                # del olx

    import time
    start = time.time()
    print('time', start)
    thr_1 = Thread(target=process, args=(list_pages[0:20],))
    thr_1.start()
    thr_1.join()
    end = time.time()
    print('end', end - start)
    return JsonResponse(dict(status='success'))
