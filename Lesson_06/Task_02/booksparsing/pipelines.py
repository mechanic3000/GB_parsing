# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


class BooksparsingPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client.books

    def process_item(self, item, spider):

        try:
            item['main_price'] = float(item['main_price'])
        except TypeError:
            item['main_price'] = None
        try:
            item['cur_price'] = float(item['cur_price'])
        except TypeError:
            item['cur_price'] = None

        item['rating'] = float(item['rating'])

        collection = self.mongobase[spider.name]
        collection.insert_one(item)

        return item
