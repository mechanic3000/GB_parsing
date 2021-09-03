# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
from itemadapter import ItemAdapter
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline
import os
from urllib.parse import urlparse


class HomegoodsPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client.homegoods

    def process_item(self, item, spider):
        collection = self.mongobase[spider.name]
        collection.insert_one(item)
        return item


class HomegoodsPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img_link in item['photos']:
                try:
                    yield scrapy.Request(img_link)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [_[1] for _ in results if _[0]]
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        return f"{item['name']}/{os.path.basename(urlparse(request.url).path)}"
