import requests
from pymongo import MongoClient
from lxml import html
import time
import random as rnd
from datetime import datetime


client = MongoClient('localhost', 27017)
db = client['news']
news_db = db.news_list


def to_base_with_check(data, connection):
    do = True
    for _ in connection.find({'link': data['link']}):
        do = False
    if do:
        connection.insert_one(data)
    return do


counter = 0

url = 'https://mail.ru/'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/92.0.4515.159 Safari/537.36',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;'
                     'q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'}

response = requests.get(url, headers=headers)

dom = html.fromstring(response.text)

items = dom.xpath("//ul[@data-testid='news-content']/li//a[contains(@class, 'news-visited')]/@href")

for i, item in enumerate(items):
    print(f"Reading {i+1} news...")
    news = {}
    time.sleep(rnd.randint(2, 5))  # притормозить процесс

    news_page_response = requests.get(item, headers=headers)
    news_page_dom = html.fromstring(news_page_response.text)

    title = news_page_dom.xpath("//h1[@class='hdr__inner']/text()")
    intro = news_page_dom.xpath("//div[contains(@class, 'article__intro')]/p/text()")

    maker = news_page_dom.xpath("//span[contains(text(),'источник:')]/following-sibling::a/span/text()")
    date = news_page_dom.xpath(".//div[contains(@class, 'breadcrumbs')]//span[1]/span[1]/span[1]/@datetime")

    if len(title) > 0 and len(intro) > 0:
        news['title'] = title[0]
        news['intro'] = intro[0]
        news['date'] = datetime.fromisoformat(date[0])
        news['maker'] = maker[0]
        news['link'] = item

        print('Done')
        if to_base_with_check(news, news_db):
            counter += 1
    else:
        print('Skipped')

print(f'{counter} news added to DB')
