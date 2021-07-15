# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Field
from scrapy import Item


class JobparserItem(Item):
    # *Наименование вакансии
    name = Field()
    # *Зарплата от
    # *Зарплата до
    salary = Field()
    # *Ссылку на саму вакансию
    link = Field()
    # *Сайт откуда собрана вакансия
    source_site = Field()
