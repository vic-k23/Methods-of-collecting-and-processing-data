# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
from config import get_config as cfg
from pymongo import MongoClient
from os.path import splitext
from urllib.parse import urlparse


class InstagramParserPipeline:
    def __init__(self):
        client = MongoClient(cfg['MongoDB']['host'],
                             int(cfg['MongoDB']['port']),
                             tz_aware=bool(cfg['MongoDB']['tz_aware']),
                             username=cfg['MongoDB']['username'],
                             password=cfg['MongoDB']['password'])
        self.db = client.instagram

    def process_item(self, item, spider):
        collection = self.db[f"{item['username']}_{item['user_id']}"]
        # document = {
        #     'friendship_type': item['friendship_type'],
        #     'friend_photo': item['friend_photo'],
        #     'friend_pk': item['friend_pk'],
        #     'friend_login': item['friend_login'],
        #     'friend_has_anonymous_profile_picture': item['friend_has_anonymous_profile_picture'],
        #     'friend_data': item['friend_data']
        # }
        item.pop('username', None)
        item.pop('user_id', None)
        # С update_one какая-то проблема: почему-то сохраняется меньше, где-то находит дубли. Ручной поиск по friend_pk
        # после выполнения скрипта с применением insert_one дублей не обнаружил. Предположение, что фильтр составлен
        # неправильно, и находятся записи с перекрёстной подпиской, тоже не подтвердилось - среди "дублей" есть записи
        # без перекрёстной подписки. В текущем виде нельзя запускать скрипт повторно по одному пользователю, потому что
        # в БД будут добавлены те же записи повторно.
        # TODO: Findout, why update_one doesn't work correctly
        # collection.update_one(
        #     {'friend_pk': item['friend_pk'],
        #      'friendship_type': item['friendship_type']},
        #     {'$set': dict(item)},
        #     upsert=True
        # )
        # if collection.count_documents({'friend_pk': item['friend_pk'], 'friendship_type': item['friendship_type']}) > 0:
        #     collection.update_one(
        #             {'friend_pk': item['friend_pk'],
        #              'friendship_type': item['friendship_type']},
        #             {'$set': dict(item)}
        #     )
        # else:
        collection.insert_one(dict(item))
        return item


class InstagramUserPhotoPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        try:
            yield Request(item['friend_photo'])
        except Exception as e:
            print(e)

    def item_completed(self, results, item, info):
        if results:
            item['friend_photo_downloaded'] = results
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        filename = f"{item['friend_login']}{splitext(urlparse(request.url).path)[1]}"
        return f"{item['username']}/{item['friendship_type']}/{filename}"
