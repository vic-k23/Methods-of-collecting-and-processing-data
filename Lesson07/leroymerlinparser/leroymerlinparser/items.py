# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst
from lxml import html


def process_characteristics(characteristic):
    characteristic_html = html.fromstring(characteristic)
    chr_name = characteristic_html.xpath('//dt/text()')[0]
    chr_val = characteristic_html.xpath('//dd/text()')[0].replace('\n', '')
    return chr_name, chr_val


def process_price(value):
    try:
        value = float(value)
    finally:
        return value



class LeroymerlinparserItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field(output_processor=TakeFirst())
    tags = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(process_price), output_processor=TakeFirst())
    link = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field(input_processor=MapCompose())
    characteristicks = scrapy.Field(input_processor=MapCompose(process_characteristics))
    # _id = scrapy.Field()
