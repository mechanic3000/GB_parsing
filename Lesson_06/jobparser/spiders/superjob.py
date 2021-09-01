import scrapy
from scrapy.http import HtmlResponse
from Lesson_06.jobparser.items import JobparserItem


class SuperjobSpider(scrapy.Spider):
    name = 'superjob'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://www.superjob.ru/vacancy/search/?keywords=python&geo%5Bt%5D%5B0%5D=4',
                  'https://www.superjob.ru/vacancy/search/?keywords=python&geo%5Br%5D%5B0%5D=2']

    def parse(self, response: HtmlResponse):
        urls = response.xpath("//div[contains(@class,'f-test-vacancy-item')]/div/div[3]/div/div/div/a/@href").getall()
        next_page_button = response.xpath("//a[contains(@class,'f-test-button-dalshe')]/@href").get()
        if next_page_button:
            yield response.follow(next_page_button, callback=self.parse)
        for url in urls:
            yield response.follow(url, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        name = response.xpath("//h1/text()").get()
        salary = response.xpath("//h1/following-sibling::span/span/span//text()").getall()
        url = response.url
        site_from = SuperjobSpider.allowed_domains[0]

        item = JobparserItem(name=name, salary=salary, url=url, site_from=site_from)
        yield item