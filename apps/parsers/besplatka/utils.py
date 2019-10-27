from lxml import html
import requests


def get_pages_sum() -> int:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    }
    body = html.document_fromstring(
        requests.get('https://besplatka.ua/transport/legkovye-avtomobili', headers=headers).text)
    return int(body.xpath('//*[@id="pagination"]/div/ul/li[14]/a/text()')[0])


def bp_slicer_of_pages(threads: int, set_sum_page=False) -> list:

    if set_sum_page:
        rest = set_sum_page // threads
    else:
        rest = get_pages_sum() // threads
    response = [(0, rest,)]
    [response.append(((page - 1) * rest + 1, rest * page)) for page in range(2, threads + 1)]
    return response
