from scrapy.settings import Settings
from scrapy.crawler import CrawlerProcess

from instaparser import settings
from instaparser.spiders.instagram import InstagramSpider
from instaparser.spiders.instagramfollowers import InstagramfollowersSpider

if __name__ == '__main__':
    crawler_setting = Settings()
    crawler_setting.setmodule(settings)

    process = CrawlerProcess(crawler_setting)
    # process.crawl(InstagramSpider)
    process.crawl(InstagramfollowersSpider)

    process.start()
