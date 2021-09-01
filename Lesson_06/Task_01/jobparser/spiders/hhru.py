import scrapy
from scrapy.http import HtmlResponse
from Lesson_06.Task_01.jobparser.items import JobparserItem


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?clusters=true&area=1&text=Python',
                  'https://spb.hh.ru/search/vacancy?clusters=true&area=2&text=Python']

    def parse(self, response: HtmlResponse):
        urls = response.xpath("//a[@data-qa='vacancy-serp__vacancy-title']/@href").getall()
        next_page_button = response.xpath("//a[@data-qa='pager-next']/@href").get()
        if next_page_button:
            yield response.follow(next_page_button, callback=self.parse)
        for url in urls:
            yield response.follow(url, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        name = response.xpath("//h1[@data-qa='vacancy-title']/text()").get()
        # salary = response.xpath("//p[@class='vacancy-salary']/span/text()").get()
        salary = response.css("p.vacancy-salary span::text").get()
        url = response.url
        site_from = HhruSpider.allowed_domains[0]

        item = JobparserItem(name=name, salary=salary, url=url, site_from=site_from)
        yield item


