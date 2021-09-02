from scrapy.settings import Settings
from scrapy.crawler import CrawlerProcess

from Lesson_06.Task_01.jobparser import settings
# from Lesson_06.Task_01.jobparser.spiders.hhru import HhruSpider
from Lesson_06.Task_01.jobparser.spiders.superjob import SuperjobSpider

if __name__ == '__main__':
    crawler_setting = Settings()
    crawler_setting.setmodule(settings)

    process = CrawlerProcess(crawler_setting)
    # process.crawl(HhruSpider)
    process.crawl(SuperjobSpider)

    process.start()
