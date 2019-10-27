from django.http import JsonResponse
from threading import Thread
from time import sleep

from apps.parsers.besplatka.utils import get_pages_sum, bp_slicer_of_pages
from .parser import Besplatka
from django.views import View


class Bsp(View):
    def get(self, req):
        # bp_slicer_of_pages(3)
        thrs = []
        for pages in bp_slicer_of_pages(1):
            bp = Besplatka()
            thr = Thread(target=bp.run, args=(pages[0], pages[1]))
            print('hi')
            thr.start()
            thrs.append(thr)
        for thr in thrs:
            thr.join()
        return JsonResponse({'status': 'success'})


        # scan = {
        #     'count_pages': 0,
        #     'current_page': 0,
        # }
        #
        # # Реализация многопоточности
        # def processing(scan, thread_num):
        #     bsp = Besplatka()
        #     # print('Thread {0} started'.format(thread_num))
        #     while 1:
        #         # print('count_pages', scan['count_pages'])
        #         # print('current_page', scan['current_page'])
        #         # print('thread_num', thread_num)
        #         if scan['count_pages'] <= scan['current_page'] and thread_num == 0:
        #             scan['count_pages'] = bsp.get_count_pages()
        #             scan['current_page'] = 0
        #         elif scan['count_pages'] <= scan['current_page']:
        #             # print('Thread {0} sleep 10 seconds ({1} <= {2})'.format(thread_num, scan['count_pages'],
        #                                                                     # scan['current_page']))
        #             sleep(10)
        #             continue
        #
        #         scan['current_page'] += 1
        #         # print('Scan page: {0} Thread num: {1}'.format(scan['current_page'], thread_num))
        #
        #         list_urls = bsp.get_urls_by_page(scan['current_page'])
        #         for url in list_urls:
        #             bsp.get_info_by_url(url)
        #     print('End thread')
        #
        # count_threads = 3
        # threads = []
        #
        # for i in range(count_threads):
        #     thread = Thread(target=processing, args=(scan, i,))
        #     thread.start()
        #     threads.append(thread)
        #
        # for t in threads:
        #     t.join()
        #
        # print("Exiting Main Thread")
        # return JsonResponse({'status': 'success'})
