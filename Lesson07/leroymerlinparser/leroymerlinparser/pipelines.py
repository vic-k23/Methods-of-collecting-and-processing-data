# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
from config import get_config as cfg
from pymongo import MongoClient
from os.path import basename
from urllib.parse import urlparse


class LeroymerlinparserPipeline:
    def __init__(self):
        client = MongoClient(cfg['MongoDB']['host'],
                             int(cfg['MongoDB']['port']),
                             tz_aware=bool(cfg['MongoDB']['tz_aware']),
                             username=cfg['MongoDB']['username'],
                             password=cfg['MongoDB']['password'])
        self.db = client.leroymerlin

    def process_item(self, item, spider):

        collection = self.db[spider.catalog]
        collection.update_one({'link': item['link']}, {'$set': dict(item)}, upsert=True)
        return item


class LeroymerlinPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield Request(img)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [itm[1] for itm in results if itm[0]]
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        return f"{item['tags']}/{item['name']}/{basename(urlparse(request.url).path)}"
