from scrapy.settings import Settings
from scrapy.crawler import CrawlerProcess

from homegoods import settings
from homegoods.spiders.leroymerlin import LeroymerlinSpider

if __name__ == '__main__':
    crawler_setting = Settings()
    crawler_setting.setmodule(settings)

    process = CrawlerProcess(crawler_setting)
    query_str = input("Введите название категории товаров: ")
    process.crawl(LeroymerlinSpider, query_str=query_str)

    process.start()
