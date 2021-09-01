# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BooksparsingItem(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()
    authors = scrapy.Field()
    main_price = scrapy.Field()
    cur_price = scrapy.Field()
    rating = scrapy.Field()
    _id = scrapy.Field()
