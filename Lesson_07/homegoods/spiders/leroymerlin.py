import scrapy
from scrapy.http import HtmlResponse
from ..items import HomegoodsItem
from scrapy.loader import ItemLoader

class LeroymerlinSpider(scrapy.Spider):
    name = 'leroymerlin'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, query_str, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [f'https://leroymerlin.ru/search/?q={query_str}']

    def parse(self, response: HtmlResponse, **kwargs):
        urls = response.xpath("//a[@data-qa='product-name']")
        next_page_button = response.xpath("//a[@data-qa-pagination-item='right']/@href").get()
        if next_page_button:
            yield response.follow(next_page_button, callback=self.parse)
        for url in urls:
            yield response.follow(url, callback=self.parse_goods)


    def parse_goods(self, response: HtmlResponse):
        loader = ItemLoader(item=HomegoodsItem(), response=response)
        loader.add_xpath("name", "//h1/text()")
        loader.add_xpath("photos", "//img[@slot='thumbs']/@src")
        loader.add_xpath("description", "//section[@id='nav-description']//p/parent::div")
        options = {}
        for option in response.xpath("//div[@class='def-list__group']"):
            options[option.xpath("./dt/text()").get()] = option.xpath("./dd/text()").get()
        loader.add_value("options", options)
        loader.add_value("link", response.url)
        loader.add_xpath("price", "//span[@slot='price']/text()")

        yield loader.load_item()
