from scrapy.settings import Settings
from scrapy.crawler import CrawlerProcess

from booksparsing import settings
from booksparsing.spiders.labirintru import LabirintruSpider


if __name__ == '__main__':
    crawler_setting = Settings()
    crawler_setting.setmodule(settings)

    process = CrawlerProcess(crawler_setting)
    process.crawl(LabirintruSpider)

    process.start()
