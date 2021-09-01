import scrapy
from scrapy.http import HtmlResponse
from ..items import BooksparsingItem


class LabirintruSpider(scrapy.Spider):
    name = 'labirintru'
    allowed_domains = ['labirint.ru']
    start_urls = ['https://www.labirint.ru/books/']

    def parse(self, response: HtmlResponse):
        urls = response.xpath("//div[@class='filters-selected']/following-sibling::div//"
                              "div[contains(@class, 'column_gutter')][not (contains(@class, 'responsive-promoblock'))]"
                              "//a[@class='product-title-link']/@href").getall()
        next_page_button = response.xpath("//div[@class='pagination-next']/a/@href").get()

        if next_page_button:
            yield response.follow(next_page_button, callback=self.parse)

        for url in urls:
            yield response.follow(url, callback=self.book_parse)


    def book_parse(self, response: HtmlResponse):
        title = response.xpath("//h1/text()").get()
        link = response.url
        authors = response.xpath("//div[@class='product-description']//a[@data-event-label='author']/text()").getall()
        main_price = response.xpath("//span[@class='buying-priceold-val-number']/text()").get()
        cur_price = response.xpath("//span[@class='buying-price-val-number']/text()").get()
        rating = response.xpath("//div[@id='rate']/text()").get()

        item = BooksparsingItem(title=title, link=link, authors=authors, main_price=main_price, cur_price=cur_price,
                                rating=rating)
        yield item

