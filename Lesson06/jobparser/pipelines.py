# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


from scrapy import Spider
from pymongo import MongoClient
from re import search
from .config import get_config as cfg
from logging import getLogger


class JobparserPipeline:
    def __init__(self):
        client = MongoClient(cfg['MongoDB']['host'],
                             int(cfg['MongoDB']['port']),
                             tz_aware=bool(cfg['MongoDB']['tz_aware']),
                             username=cfg['MongoDB']['username'],
                             password=cfg['MongoDB']['password'])
        self.db = client.vacancies
        self.log = getLogger(__name__)

    def process_item(self, item, spider: Spider):
        item['salary'] = self.process_salary(item['salary'])
        # item['source_site'] = search(r'(https?://\w+\.\w{2,3}/).*', item['link']).groups()[0]
        collection = self.db[spider.name]
        collection.update_one({'link': item['link']}, {'$set': dict(item)}, upsert=True)

        return item

    def process_salary(self, salary: str):
        if not isinstance(salary, str) or salary is None:
            return [None, None, None]
        lst_salary = \
            search(r'^(?:[от|до]+\s+)?(\d+\s?\d*)?(?:\s+до)?(?:\s+)?(\d+\s?\d*)?(?:\s+)([a-zA-Zа-яА-ЯёЁ]+)(?:\s\.*)?',
                   salary.replace('\xa0', ' '))
        if lst_salary is None:
            return [None, None, None]
        else:
            lst_salary = list(lst_salary.groups())
        try:
            if lst_salary[0] is not None:
                lst_salary[0] = float(lst_salary[0].replace(' ', ''))
            if lst_salary[1] is not None:
                lst_salary[1] = float(lst_salary[1].replace(' ', ''))
        except AttributeError:
            self.log.error("Не удалось преобразовать значение зарплаты.")
        finally:
            return lst_salary
